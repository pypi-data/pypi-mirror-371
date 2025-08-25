# Copyright (c) 2025, The pywebtransport Authors.
# All rights reserved.
#
# This file is part of the pywebtransport project. It is licensed under the MIT License.
# See the LICENSE file in the project root for full license text.

# --- Attribution Notice ---
#
# NOTE:
# This file was originally derived from aioquic's `h3/connection.py`
# (aioquic version 1.2.0, forked on 2025-07-01). It has been heavily modified
# and specialized by the pywebtransport authors to serve exclusively as a
# WebTransport-over-H3 protocol engine.
#
# It no longer shares code or architecture with upstream aioquic and
# is now maintained independently under the pywebtransport project.
#
# The original aioquic license and copyright notice are retained below as
# required by the BSD 3-Clause license.

# --- Original aioquic License ---
#
# Copyright (c) Jeremy Lainé.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of aioquic nor the names of its contributors may
#       be used to endorse or promote products derived from this software without
#       specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
HTTP/3 Protocol Implementation with WebTransport Extensions.
"""

from __future__ import annotations

import logging
import re
from enum import Enum, IntEnum
from typing import FrozenSet

import pylsqpack
from aioquic.buffer import UINT_VAR_MAX_SIZE, Buffer, BufferReadError, encode_uint_var
from aioquic.h3.events import (
    DatagramReceived,
    DataReceived,
    H3Event,
    Headers,
    HeadersReceived,
    PushPromiseReceived,
    WebTransportStreamDataReceived,
)
from aioquic.h3.exceptions import InvalidStreamTypeError, NoAvailablePushIDError
from aioquic.quic.connection import QuicConnection, stream_is_unidirectional
from aioquic.quic.events import DatagramFrameReceived, QuicEvent, StreamDataReceived
from aioquic.quic.logger import QuicLoggerTrace

logger = logging.getLogger("http3")

H3_ALPN = ["h3"]
RESERVED_SETTINGS = (0x0, 0x2, 0x3, 0x4, 0x5)
UPPERCASE = re.compile(b"[A-Z]")
COLON = 0x3A
NUL = 0x00
LF = 0x0A
CR = 0x0D
SP = 0x20
HTAB = 0x09
WHITESPACE = (SP, HTAB)


class ErrorCode(IntEnum):
    H3_DATAGRAM_ERROR = 0x33
    H3_NO_ERROR = 0x100
    H3_GENERAL_PROTOCOL_ERROR = 0x101
    H3_INTERNAL_ERROR = 0x102
    H3_STREAM_CREATION_ERROR = 0x103
    H3_CLOSED_CRITICAL_STREAM = 0x104
    H3_FRAME_UNEXPECTED = 0x105
    H3_FRAME_ERROR = 0x106
    H3_EXCESSIVE_LOAD = 0x107
    H3_ID_ERROR = 0x108
    H3_SETTINGS_ERROR = 0x109
    H3_MISSING_SETTINGS = 0x10A
    H3_REQUEST_REJECTED = 0x10B
    H3_REQUEST_CANCELLED = 0x10C
    H3_REQUEST_INCOMPLETE = 0x10D
    H3_MESSAGE_ERROR = 0x10E
    H3_CONNECT_ERROR = 0x10F
    H3_VERSION_FALLBACK = 0x110
    QPACK_DECOMPRESSION_FAILED = 0x200
    QPACK_ENCODER_STREAM_ERROR = 0x201
    QPACK_DECODER_STREAM_ERROR = 0x202


class FrameType(IntEnum):
    DATA = 0x0
    HEADERS = 0x1
    PRIORITY = 0x2
    CANCEL_PUSH = 0x3
    SETTINGS = 0x4
    PUSH_PROMISE = 0x5
    GOAWAY = 0x7
    MAX_PUSH_ID = 0xD
    DUPLICATE_PUSH = 0xE
    WEBTRANSPORT_STREAM = 0x41


class HeadersState(Enum):
    INITIAL = 0
    AFTER_HEADERS = 1
    AFTER_TRAILERS = 2


class Setting(IntEnum):
    QPACK_MAX_TABLE_CAPACITY = 0x1
    MAX_FIELD_SECTION_SIZE = 0x6
    QPACK_BLOCKED_STREAMS = 0x7
    ENABLE_CONNECT_PROTOCOL = 0x8
    H3_DATAGRAM = 0x33
    ENABLE_WEBTRANSPORT = 0x2B603742
    DUMMY = 0x21


class StreamType(IntEnum):
    CONTROL = 0
    PUSH = 1
    QPACK_ENCODER = 2
    QPACK_DECODER = 3
    WEBTRANSPORT = 0x54


class ProtocolError(Exception):
    """Base class for H3 protocol errors handled internally."""

    error_code = ErrorCode.H3_GENERAL_PROTOCOL_ERROR

    def __init__(self, reason_phrase: str = ""):
        self.reason_phrase = reason_phrase


class ClosedCriticalStream(ProtocolError):
    error_code = ErrorCode.H3_CLOSED_CRITICAL_STREAM


class DatagramError(ProtocolError):
    error_code = ErrorCode.H3_DATAGRAM_ERROR


class FrameUnexpected(ProtocolError):
    error_code = ErrorCode.H3_FRAME_UNEXPECTED


class MessageError(ProtocolError):
    error_code = ErrorCode.H3_MESSAGE_ERROR


class MissingSettingsError(ProtocolError):
    error_code = ErrorCode.H3_MISSING_SETTINGS


class QpackDecompressionFailed(ProtocolError):
    error_code = ErrorCode.QPACK_DECOMPRESSION_FAILED


class QpackDecoderStreamError(ProtocolError):
    error_code = ErrorCode.QPACK_DECODER_STREAM_ERROR


class QpackEncoderStreamError(ProtocolError):
    error_code = ErrorCode.QPACK_ENCODER_STREAM_ERROR


class SettingsError(ProtocolError):
    error_code = ErrorCode.H3_SETTINGS_ERROR


class StreamCreationError(ProtocolError):
    error_code = ErrorCode.H3_STREAM_CREATION_ERROR


def encode_frame(frame_type: int, frame_data: bytes) -> bytes:
    """Encode a raw H3 frame."""
    frame_length = len(frame_data)
    buf = Buffer(capacity=frame_length + 2 * UINT_VAR_MAX_SIZE)
    buf.push_uint_var(frame_type)
    buf.push_uint_var(frame_length)
    buf.push_bytes(frame_data)
    return buf.data


def encode_settings(settings: dict[int, int]) -> bytes:
    """Encode a SETTINGS frame payload."""
    buf = Buffer(capacity=1024)
    for setting, value in settings.items():
        buf.push_uint_var(setting)
        buf.push_uint_var(value)
    return buf.data


def parse_max_push_id(data: bytes) -> int:
    """Parse a MAX_PUSH_ID frame payload."""
    buf = Buffer(data=data)
    max_push_id = buf.pull_uint_var()
    assert buf.eof()
    return max_push_id


def parse_settings(data: bytes) -> dict[int, int]:
    """Parse a SETTINGS frame payload."""
    buf = Buffer(data=data)
    settings: dict[int, int] = {}
    while not buf.eof():
        setting = buf.pull_uint_var()
        value = buf.pull_uint_var()
        if setting in RESERVED_SETTINGS:
            raise SettingsError(f"Setting identifier 0x{setting:x} is reserved")
        if setting in settings:
            raise SettingsError(f"Setting identifier 0x{setting:x} is included twice")
        settings[setting] = value
    return dict(settings)


def stream_is_request_response(stream_id: int) -> bool:
    """Return True if the stream is a client-initiated bidirectional stream."""
    return stream_id % 4 == 0


def validate_header_name(key: bytes) -> None:
    """Validate an individual header name."""
    for i, c in enumerate(key):
        if c <= 0x20 or (c >= 0x41 and c <= 0x5A) or c >= 0x7F:
            raise MessageError(f"Header {key!r} contains invalid characters")
        if c == COLON and i != 0:
            raise MessageError(f"Header {key!r} contains a non-initial colon")


def validate_header_value(key: bytes, value: bytes) -> None:
    """Validate an individual header value."""
    for c in value:
        if c == NUL or c == LF or c == CR:
            raise MessageError(f"Header {key!r} value has forbidden characters")
    if len(value) > 0:
        if value[0] in WHITESPACE:
            raise MessageError(f"Header {key!r} value starts with whitespace")
        if len(value) > 1 and value[-1] in WHITESPACE:
            raise MessageError(f"Header {key!r} value ends with whitespace")


def validate_headers(
    headers: Headers,
    allowed_pseudo_headers: FrozenSet[bytes],
    required_pseudo_headers: FrozenSet[bytes],
    stream: H3Stream | None = None,
) -> None:
    """Validate a list of headers."""
    after_pseudo_headers = False
    authority: bytes | None = None
    path: bytes | None = None
    scheme: bytes | None = None
    seen_pseudo_headers: set[bytes] = set()
    for key, value in headers:
        validate_header_name(key)
        validate_header_value(key, value)

        if key.startswith(b":"):
            if after_pseudo_headers:
                raise MessageError(f"Pseudo-header {key!r} is not allowed after regular headers")
            if key not in allowed_pseudo_headers:
                raise MessageError(f"Pseudo-header {key!r} is not valid")
            if key in seen_pseudo_headers:
                raise MessageError(f"Pseudo-header {key!r} is included twice")
            seen_pseudo_headers.add(key)
            if key == b":authority":
                authority = value
            elif key == b":path":
                path = value
            elif key == b":scheme":
                scheme = value
        else:
            after_pseudo_headers = True
            if key == b"content-length":
                try:
                    content_length = int(value)
                    if content_length < 0:
                        raise ValueError
                except ValueError:
                    raise MessageError("content-length is not a non-negative integer")
                if stream:
                    stream.expected_content_length = content_length
            elif key == b"transfer-encoding" and value != b"trailers":
                raise MessageError("The only valid value for transfer-encoding is trailers")

    missing = required_pseudo_headers.difference(seen_pseudo_headers)
    if missing:
        raise MessageError(f"Pseudo-headers {sorted(missing)} are missing")

    if scheme in (b"http", b"https"):
        if not authority:
            raise MessageError("Pseudo-header b':authority' cannot be empty")
        if not path:
            raise MessageError("Pseudo-header b':path' cannot be empty")


def validate_push_promise_headers(headers: Headers) -> None:
    """Validate headers for a PUSH_PROMISE frame."""
    validate_headers(
        headers,
        allowed_pseudo_headers=frozenset((b":method", b":scheme", b":authority", b":path")),
        required_pseudo_headers=frozenset((b":method", b":scheme", b":authority", b":path")),
    )


def validate_request_headers(headers: Headers, stream: H3Stream | None = None) -> None:
    """Validate headers for a request."""
    validate_headers(
        headers,
        allowed_pseudo_headers=frozenset((b":method", b":scheme", b":authority", b":path", b":protocol")),
        required_pseudo_headers=frozenset((b":method", b":authority")),
        stream=stream,
    )


def validate_response_headers(headers: Headers, stream: H3Stream | None = None) -> None:
    """Validate headers for a response."""
    validate_headers(
        headers,
        allowed_pseudo_headers=frozenset((b":status",)),
        required_pseudo_headers=frozenset((b":status",)),
        stream=stream,
    )


def validate_trailers(headers: Headers) -> None:
    """Validate trailer headers."""
    validate_headers(
        headers,
        allowed_pseudo_headers=frozenset(),
        required_pseudo_headers=frozenset(),
    )


class H3Stream:
    """Represents the state of a single H3 stream."""

    def __init__(self, stream_id: int) -> None:
        """Initialize an H3 stream."""
        self.blocked = False
        self.blocked_frame_size: int | None = None
        self.buffer = b""
        self.ended = False
        self.frame_size: int | None = None
        self.frame_type: int | None = None
        self.headers_recv_state: HeadersState = HeadersState.INITIAL
        self.headers_send_state: HeadersState = HeadersState.INITIAL
        self.push_id: int | None = None
        self.session_id: int | None = None
        self.stream_id = stream_id
        self.stream_type: int | None = None
        self.expected_content_length: int | None = None
        self.content_length: int = 0


class H3Connection:
    """A low-level HTTP/3 connection object."""

    def __init__(self, quic: QuicConnection, enable_webtransport: bool = False) -> None:
        """Initialize an H3 connection."""
        self._max_table_capacity = 4096
        self._blocked_streams = 16
        self._enable_webtransport = enable_webtransport
        self._is_client = quic.configuration.is_client
        self._is_done = False
        self._quic = quic
        self._quic_logger: QuicLoggerTrace | None = quic._quic_logger
        self._decoder = pylsqpack.Decoder(self._max_table_capacity, self._blocked_streams)
        self._decoder_bytes_received = 0
        self._decoder_bytes_sent = 0
        self._encoder = pylsqpack.Encoder()
        self._encoder_bytes_received = 0
        self._encoder_bytes_sent = 0
        self._settings_received = False
        self._stream: dict[int, H3Stream] = {}
        self._max_push_id: int | None = 8 if self._is_client else None
        self._next_push_id: int = 0
        self._local_control_stream_id: int | None = None
        self._local_decoder_stream_id: int | None = None
        self._local_encoder_stream_id: int | None = None
        self._peer_control_stream_id: int | None = None
        self._peer_decoder_stream_id: int | None = None
        self._peer_encoder_stream_id: int | None = None
        self._received_settings: dict[int, int] | None = None
        self._sent_settings: dict[int, int] | None = None
        self._init_connection()

    @property
    def received_settings(self) -> dict[int, int] | None:
        """Return the received SETTINGS frame, or None."""
        return self._received_settings

    @property
    def sent_settings(self) -> dict[int, int] | None:
        """Return the sent SETTINGS frame, or None."""
        return self._sent_settings

    def create_webtransport_stream(self, session_id: int, is_unidirectional: bool = False) -> int:
        """Create a WebTransport stream and return the stream ID."""
        if is_unidirectional:
            stream_id = self._create_uni_stream(StreamType.WEBTRANSPORT)
            # PYWT_ADAPT: Add support for creating unidirectional WebTransport streams.
            # REASON: The original aioquic H3 did not recognize the WT-specific
            #         unidirectional stream type (0x54).
            # FIX:    A new stream of type WEBTRANSPORT is created, and the session
            #         ID is sent as its initial raw data payload, as per the spec.
            stream = self._get_or_create_stream(stream_id)
            stream.session_id = session_id
            stream.stream_type = StreamType.WEBTRANSPORT
            self._quic.send_stream_data(stream_id, encode_uint_var(session_id))
        else:
            stream_id = self._quic.get_next_available_stream_id()
            # PYWT_ADAPT: Add support for creating bidirectional WebTransport streams.
            # REASON: The original aioquic H3 had no mechanism to send the
            #         WEBTRANSPORT_STREAM (0x41) setup frame required by the protocol.
            # FIX:    A new bidirectional stream is created, its local state is
            #         marked as a WT stream, and the 0x41 setup frame containing
            #         the session ID is sent to the peer.
            stream = self._get_or_create_stream(stream_id)
            stream.session_id = session_id
            stream.stream_type = StreamType.WEBTRANSPORT
            self._log_stream_type(stream_id=stream_id, stream_type=StreamType.WEBTRANSPORT)
            self._quic.send_stream_data(
                stream_id,
                encode_uint_var(FrameType.WEBTRANSPORT_STREAM) + encode_uint_var(session_id),
            )
        return stream_id

    def handle_event(self, event: QuicEvent) -> list[H3Event]:
        """Handle a QUIC event and return a list of HTTP events."""
        if not self._is_done:
            try:
                if isinstance(event, StreamDataReceived):
                    stream_id = event.stream_id
                    stream = self._get_or_create_stream(stream_id)
                    if stream_is_unidirectional(stream_id):
                        return self._receive_stream_data_uni(stream, event.data, event.end_stream)
                    else:
                        return self._receive_request_or_push_data(stream, event.data, event.end_stream)
                elif isinstance(event, DatagramFrameReceived):
                    return self._receive_datagram(event.data)
            except ProtocolError as exc:
                self._is_done = True
                self._quic.close(error_code=exc.error_code, reason_phrase=exc.reason_phrase)
        return []

    def send_data(self, stream_id: int, data: bytes, end_stream: bool) -> None:
        """Send data on the given stream."""
        stream = self._get_or_create_stream(stream_id)
        # PYWT_ADAPT: Bypass H3 DATA frame encapsulation for WebTransport streams.
        # REASON: The original code would unconditionally wrap payload in an H3
        #         DATA frame, which violates the WebTransport protocol's requirement
        #         for sending raw data after the session is established.
        # FIX:    By checking `stream.session_id`, we identify WT streams and send
        #         their data directly to the QUIC layer, bypassing H3 framing.
        if stream.session_id is not None:
            if data or end_stream:
                self._quic.send_stream_data(stream_id, data, end_stream)
            return

        if stream.headers_send_state != HeadersState.AFTER_HEADERS:
            raise FrameUnexpected("DATA frame is not allowed in this state")
        if self._quic_logger is not None:
            self._quic_logger.log_event(
                category="http",
                event="frame_created",
                data=self._quic_logger.encode_http3_data_frame(length=len(data), stream_id=stream_id),
            )
        self._quic.send_stream_data(stream_id, encode_frame(FrameType.DATA, data), end_stream)

    def send_datagram(self, stream_id: int, data: bytes) -> None:
        """Send a datagram for the specified stream."""
        if not stream_is_request_response(stream_id):
            raise InvalidStreamTypeError("Datagrams can only be sent for client-initiated bidirectional streams")
        self._quic.send_datagram_frame(encode_uint_var(stream_id // 4) + data)

    def send_headers(self, stream_id: int, headers: Headers, end_stream: bool = False) -> None:
        """Send headers on the given stream."""
        stream = self._get_or_create_stream(stream_id)
        if stream.headers_send_state == HeadersState.AFTER_TRAILERS:
            raise FrameUnexpected("HEADERS frame is not allowed in this state")

        frame_data = self._encode_headers(stream_id, headers)
        if self._quic_logger is not None:
            self._quic_logger.log_event(
                category="http",
                event="frame_created",
                data=self._quic_logger.encode_http3_headers_frame(
                    length=len(frame_data), headers=headers, stream_id=stream_id
                ),
            )

        if stream.headers_send_state == HeadersState.INITIAL:
            stream.headers_send_state = HeadersState.AFTER_HEADERS
        else:
            stream.headers_send_state = HeadersState.AFTER_TRAILERS
        self._quic.send_stream_data(stream_id, encode_frame(FrameType.HEADERS, frame_data), end_stream)

    def send_push_promise(self, stream_id: int, headers: Headers) -> int:
        """Send a push promise related to the specified stream."""
        assert not self._is_client, "Only servers may send a push promise."
        if not stream_is_request_response(stream_id):
            raise InvalidStreamTypeError("Push promises can only be sent for client-initiated bidirectional streams")
        if self._max_push_id is None or self._next_push_id >= self._max_push_id:
            raise NoAvailablePushIDError

        push_id = self._next_push_id
        self._next_push_id += 1
        self._quic.send_stream_data(
            stream_id,
            encode_frame(FrameType.PUSH_PROMISE, encode_uint_var(push_id) + self._encode_headers(stream_id, headers)),
        )

        push_stream_id = self._create_uni_stream(StreamType.PUSH, push_id=push_id)
        self._quic.send_stream_data(push_stream_id, encode_uint_var(push_id))
        return push_stream_id

    def _check_content_length(self, stream: H3Stream) -> None:
        """Verify the received content length matches the expected length."""
        if stream.expected_content_length is not None and stream.content_length != stream.expected_content_length:
            raise MessageError("content-length does not match data size")

    def _create_uni_stream(self, stream_type: int, push_id: int | None = None) -> int:
        """Create a unidirectional stream of the given type."""
        stream_id = self._quic.get_next_available_stream_id(is_unidirectional=True)
        self._log_stream_type(push_id=push_id, stream_id=stream_id, stream_type=stream_type)
        self._quic.send_stream_data(stream_id, encode_uint_var(stream_type))
        return stream_id

    def _decode_headers(self, stream_id: int, frame_data: bytes | None) -> Headers:
        """Decode a HEADERS block and send QPACK decoder updates."""
        try:
            if frame_data is None:
                decoder, headers = self._decoder.resume_header(stream_id)
            else:
                decoder, headers = self._decoder.feed_header(stream_id, frame_data)
            self._decoder_bytes_sent += len(decoder)
            if self._local_decoder_stream_id is not None:
                self._quic.send_stream_data(self._local_decoder_stream_id, decoder)
        except pylsqpack.DecompressionFailed as exc:
            raise QpackDecompressionFailed() from exc
        return headers

    def _encode_headers(self, stream_id: int, headers: Headers) -> bytes:
        """Encode a HEADERS block and send QPACK encoder updates."""
        encoder, frame_data = self._encoder.encode(stream_id, headers)
        self._encoder_bytes_sent += len(encoder)
        if self._local_encoder_stream_id is not None:
            self._quic.send_stream_data(self._local_encoder_stream_id, encoder)
        return frame_data

    def _get_local_settings(self) -> dict[int, int]:
        """Return the local HTTP/3 settings."""
        settings: dict[int, int] = {
            Setting.QPACK_MAX_TABLE_CAPACITY: self._max_table_capacity,
            Setting.QPACK_BLOCKED_STREAMS: self._blocked_streams,
            Setting.ENABLE_CONNECT_PROTOCOL: 1,
            Setting.DUMMY: 1,
        }
        if self._enable_webtransport:
            settings[Setting.H3_DATAGRAM] = 1
            settings[Setting.ENABLE_WEBTRANSPORT] = 1
        return settings

    def _get_or_create_stream(self, stream_id: int) -> H3Stream:
        """Get an existing H3 stream or create a new one."""
        if stream_id not in self._stream:
            self._stream[stream_id] = H3Stream(stream_id)
        return self._stream[stream_id]

    def _handle_control_frame(self, frame_type: int, frame_data: bytes) -> None:
        """Handle a frame received on the peer's control stream."""
        if frame_type != FrameType.SETTINGS and not self._settings_received:
            raise MissingSettingsError
        if frame_type == FrameType.SETTINGS:
            if self._settings_received:
                raise FrameUnexpected("SETTINGS have already been received")
            settings = parse_settings(frame_data)
            self._validate_settings(settings)
            self._received_settings = settings
            encoder = self._encoder.apply_settings(
                max_table_capacity=settings.get(Setting.QPACK_MAX_TABLE_CAPACITY, 0),
                blocked_streams=settings.get(Setting.QPACK_BLOCKED_STREAMS, 0),
            )
            if self._local_encoder_stream_id is not None:
                self._quic.send_stream_data(self._local_encoder_stream_id, encoder)
            self._settings_received = True
        elif frame_type == FrameType.MAX_PUSH_ID:
            if self._is_client:
                raise FrameUnexpected("Servers must not send MAX_PUSH_ID")
            self._max_push_id = parse_max_push_id(frame_data)
        elif frame_type in (FrameType.DATA, FrameType.HEADERS, FrameType.PUSH_PROMISE, FrameType.DUPLICATE_PUSH):
            raise FrameUnexpected("Invalid frame type on control stream")

    def _handle_request_or_push_frame(
        self, frame_type: int, frame_data: bytes | None, stream: H3Stream, stream_ended: bool
    ) -> list[H3Event]:
        """Handle a frame received on a request or push stream."""
        http_events: list[H3Event] = []
        if frame_type == FrameType.DATA:
            # PYWT_ADAPT: Relax the HEADERS-first requirement for WebTransport.
            # REASON: Standard H3 requires a HEADERS frame before any DATA frames.
            #         WebTransport streams have no HEADERS and send data directly,
            #         which would cause a `FrameUnexpected` error.
            # FIX:    This check is now scoped to non-WT streams (`session_id` is None),
            #         allowing WT streams to correctly receive data without HEADERS.
            if stream.session_id is None and stream.headers_recv_state != HeadersState.AFTER_HEADERS:
                raise FrameUnexpected("DATA frame is not allowed in this state")
            if frame_data is not None:
                stream.content_length += len(frame_data)
            if stream_ended:
                self._check_content_length(stream)
            if stream_ended or frame_data:
                http_events.append(
                    DataReceived(
                        data=frame_data if frame_data is not None else b"",
                        push_id=stream.push_id,
                        stream_ended=stream_ended,
                        stream_id=stream.stream_id,
                    )
                )
        elif frame_type == FrameType.HEADERS:
            if stream.headers_recv_state == HeadersState.AFTER_TRAILERS:
                raise FrameUnexpected("HEADERS frame is not allowed in this state")
            headers = self._decode_headers(stream.stream_id, frame_data)
            if stream.headers_recv_state == HeadersState.INITIAL:
                if self._is_client:
                    validate_response_headers(headers, stream)
                else:
                    validate_request_headers(headers, stream)
            else:
                validate_trailers(headers)
            if stream_ended:
                self._check_content_length(stream)
            if self._quic_logger is not None:
                length = len(frame_data) if frame_data is not None else stream.blocked_frame_size
                assert length is not None, "Frame length for logging cannot be None"
                self._quic_logger.log_event(
                    category="http",
                    event="frame_parsed",
                    data=self._quic_logger.encode_http3_headers_frame(
                        length=length, headers=headers, stream_id=stream.stream_id
                    ),
                )
            if stream.headers_recv_state == HeadersState.INITIAL:
                stream.headers_recv_state = HeadersState.AFTER_HEADERS
            else:
                stream.headers_recv_state = HeadersState.AFTER_TRAILERS
            http_events.append(
                HeadersReceived(
                    headers=headers,
                    push_id=stream.push_id,
                    stream_id=stream.stream_id,
                    stream_ended=stream_ended,
                )
            )
        elif frame_type == FrameType.PUSH_PROMISE and stream.push_id is None:
            if not self._is_client:
                raise FrameUnexpected("Clients must not send PUSH_PROMISE")
            if frame_data is None:
                raise FrameUnexpected("PUSH_PROMISE frame cannot be empty")
            frame_buf = Buffer(data=frame_data)
            push_id = frame_buf.pull_uint_var()
            headers = self._decode_headers(stream.stream_id, frame_data[frame_buf.tell() :])
            validate_push_promise_headers(headers)
            if self._quic_logger is not None:
                self._quic_logger.log_event(
                    category="http",
                    event="frame_parsed",
                    data=self._quic_logger.encode_http3_push_promise_frame(
                        length=len(frame_data), headers=headers, push_id=push_id, stream_id=stream.stream_id
                    ),
                )
            http_events.append(PushPromiseReceived(headers=headers, push_id=push_id, stream_id=stream.stream_id))
        elif frame_type in (
            FrameType.PRIORITY,
            FrameType.CANCEL_PUSH,
            FrameType.SETTINGS,
            FrameType.PUSH_PROMISE,
            FrameType.GOAWAY,
            FrameType.MAX_PUSH_ID,
            FrameType.DUPLICATE_PUSH,
        ):
            raise FrameUnexpected(
                "Invalid frame type on request stream"
                if stream.push_id is None
                else "Invalid frame type on push stream"
            )

        return http_events

    def _init_connection(self) -> None:
        """Initialize the H3 connection by creating control streams."""
        self._local_control_stream_id = self._create_uni_stream(StreamType.CONTROL)
        self._sent_settings = self._get_local_settings()
        self._quic.send_stream_data(
            self._local_control_stream_id, encode_frame(FrameType.SETTINGS, encode_settings(self._sent_settings))
        )
        if self._is_client and self._max_push_id is not None:
            self._quic.send_stream_data(
                self._local_control_stream_id, encode_frame(FrameType.MAX_PUSH_ID, encode_uint_var(self._max_push_id))
            )
        self._local_encoder_stream_id = self._create_uni_stream(StreamType.QPACK_ENCODER)
        self._local_decoder_stream_id = self._create_uni_stream(StreamType.QPACK_DECODER)

    def _log_stream_type(self, stream_id: int, stream_type: int, push_id: int | None = None) -> None:
        """Log the stream type assignment."""
        if self._quic_logger is not None:
            type_name = {0: "control", 1: "push", 2: "qpack_encoder", 3: "qpack_decoder", 0x54: "webtransport"}.get(
                stream_type, "unknown"
            )
            data = {"new": type_name, "stream_id": stream_id}
            if push_id is not None:
                data["associated_push_id"] = push_id
            self._quic_logger.log_event(category="http", event="stream_type_set", data=data)

    def _receive_datagram(self, data: bytes) -> list[H3Event]:
        """Handle a raw datagram."""
        buf = Buffer(data=data)
        try:
            quarter_stream_id = buf.pull_uint_var()
        except BufferReadError:
            raise DatagramError("Could not parse quarter stream ID")
        return [DatagramReceived(data=data[buf.tell() :], stream_id=quarter_stream_id * 4)]

    def _receive_request_or_push_data(self, stream: H3Stream, data: bytes, stream_ended: bool) -> list[H3Event]:
        """Handle data received on a request or push stream."""
        http_events: list[H3Event] = []
        stream.buffer += data
        if stream_ended:
            stream.ended = True
        if stream.blocked:
            return http_events

        # PYWT_ADAPT: Stage 1 - Identify new WebTransport streams.
        # REASON: The original H3 parser does not recognize the WEBTRANSPORT_STREAM
        #         (0x41) frame and would raise a protocol error, killing the
        #         connection.
        # FIX:    For new streams (`session_id` is None), we preemptively parse
        #         the start of the buffer. If it's a WT setup frame, we mark
        #         the stream's type and session, then consume the frame from
        #         the buffer before any further processing.
        if self._enable_webtransport and stream.session_id is None:
            buf = Buffer(data=stream.buffer)
            try:
                frame_type = buf.pull_uint_var()
                if frame_type == FrameType.WEBTRANSPORT_STREAM:
                    session_id = buf.pull_uint_var()
                    stream.session_id = session_id
                    stream.stream_type = StreamType.WEBTRANSPORT
                    consumed = buf.tell()
                    stream.buffer = stream.buffer[consumed:]
                    self._log_stream_type(stream_id=stream.stream_id, stream_type=StreamType.WEBTRANSPORT)
            except BufferReadError:
                return http_events

        # PYWT_ADAPT: Stage 2 - Process established WebTransport streams.
        # REASON: Once established, WebTransport streams contain raw binary data,
        #         not H3 frames. Sending this data to the H3 frame parser below
        #         would be incorrect and could lead to errors.
        # FIX:    If the stream has been identified as WebTransport, we treat its
        #         entire buffer as a raw data payload, emit the appropriate event,
        #         and return immediately, bypassing the H3 parser.
        if stream.stream_type == StreamType.WEBTRANSPORT:
            if stream.buffer or stream_ended:
                assert stream.session_id is not None, "session_id must be set for WT streams"
                http_events.append(
                    WebTransportStreamDataReceived(
                        data=stream.buffer,
                        session_id=stream.session_id,
                        stream_id=stream.stream_id,
                        stream_ended=stream_ended,
                    )
                )
                stream.buffer = b""
            return http_events

        if (
            stream.frame_type == FrameType.DATA
            and stream.frame_size is not None
            and len(stream.buffer) < stream.frame_size
        ):
            stream.content_length += len(stream.buffer)
            http_events.append(
                DataReceived(data=stream.buffer, push_id=stream.push_id, stream_id=stream.stream_id, stream_ended=False)
            )
            stream.frame_size -= len(stream.buffer)
            stream.buffer = b""
            return http_events

        if stream_ended and not stream.buffer:
            self._check_content_length(stream)
            http_events.append(
                DataReceived(data=b"", push_id=stream.push_id, stream_id=stream.stream_id, stream_ended=True)
            )
            return http_events

        buf = Buffer(data=stream.buffer)
        consumed = 0
        while not buf.eof():
            if stream.frame_size is None:
                try:
                    stream.frame_type = buf.pull_uint_var()
                    stream.frame_size = buf.pull_uint_var()
                except BufferReadError:
                    break
                consumed = buf.tell()
                if self._quic_logger is not None and stream.frame_type == FrameType.DATA:
                    self._quic_logger.log_event(
                        category="http",
                        event="frame_parsed",
                        data=self._quic_logger.encode_http3_data_frame(
                            length=stream.frame_size, stream_id=stream.stream_id
                        ),
                    )

            if stream.frame_type is None:
                break
            chunk_size = min(stream.frame_size, buf.capacity - consumed)
            if stream.frame_type != FrameType.DATA and chunk_size < stream.frame_size:
                break

            frame_data = buf.pull_bytes(chunk_size)
            frame_type = stream.frame_type
            consumed = buf.tell()
            stream.frame_size -= chunk_size
            if not stream.frame_size:
                stream.frame_size = None
                stream.frame_type = None

            try:
                http_events.extend(
                    self._handle_request_or_push_frame(
                        frame_type=frame_type,
                        frame_data=frame_data,
                        stream=stream,
                        stream_ended=stream.ended and buf.eof(),
                    )
                )
            except pylsqpack.StreamBlocked:
                stream.blocked = True
                stream.blocked_frame_size = len(frame_data)
                break
        stream.buffer = stream.buffer[consumed:]
        return http_events

    def _receive_stream_data_uni(self, stream: H3Stream, data: bytes, stream_ended: bool) -> list[H3Event]:
        """Handle data received on a unidirectional stream."""
        http_events: list[H3Event] = []
        stream.buffer += data
        if stream_ended:
            stream.ended = True

        buf = Buffer(data=stream.buffer)
        consumed = 0
        unblocked_streams: set[int] = set()

        while stream.stream_type in (StreamType.PUSH, StreamType.CONTROL, StreamType.WEBTRANSPORT) or not buf.eof():
            if stream.stream_type is None:
                try:
                    stream.stream_type = buf.pull_uint_var()
                except BufferReadError:
                    break
                consumed = buf.tell()
                if stream.stream_type == StreamType.CONTROL:
                    if self._peer_control_stream_id is not None:
                        raise StreamCreationError("Only one control stream is allowed")
                    self._peer_control_stream_id = stream.stream_id
                elif stream.stream_type == StreamType.QPACK_DECODER:
                    if self._peer_decoder_stream_id is not None:
                        raise StreamCreationError("Only one QPACK decoder stream is allowed")
                    self._peer_decoder_stream_id = stream.stream_id
                elif stream.stream_type == StreamType.QPACK_ENCODER:
                    if self._peer_encoder_stream_id is not None:
                        raise StreamCreationError("Only one QPACK encoder stream is allowed")
                    self._peer_encoder_stream_id = stream.stream_id
                if stream.stream_type != StreamType.PUSH:
                    self._log_stream_type(stream_id=stream.stream_id, stream_type=stream.stream_type)

            if stream.stream_type == StreamType.CONTROL:
                if stream_ended:
                    raise ClosedCriticalStream("Closing control stream is not allowed")
                try:
                    frame_type = buf.pull_uint_var()
                    frame_length = buf.pull_uint_var()
                    frame_data = buf.pull_bytes(frame_length)
                except BufferReadError:
                    break
                consumed = buf.tell()
                self._handle_control_frame(frame_type, frame_data)
            elif stream.stream_type == StreamType.PUSH:
                if stream.push_id is None:
                    try:
                        stream.push_id = buf.pull_uint_var()
                    except BufferReadError:
                        break
                    consumed = buf.tell()
                    self._log_stream_type(
                        push_id=stream.push_id, stream_id=stream.stream_id, stream_type=stream.stream_type
                    )
                stream.buffer = stream.buffer[consumed:]
                return self._receive_request_or_push_data(stream, b"", stream_ended)
            elif stream.stream_type == StreamType.WEBTRANSPORT:
                if stream.session_id is None:
                    try:
                        stream.session_id = buf.pull_uint_var()
                    except BufferReadError:
                        break
                    consumed = buf.tell()
                frame_data = stream.buffer[consumed:]
                stream.buffer = b""
                if frame_data or stream_ended:
                    http_events.append(
                        WebTransportStreamDataReceived(
                            data=frame_data,
                            session_id=stream.session_id,
                            stream_ended=stream.ended,
                            stream_id=stream.stream_id,
                        )
                    )
                return http_events
            elif stream.stream_type == StreamType.QPACK_DECODER:
                data = buf.pull_bytes(buf.capacity - buf.tell())
                consumed = buf.tell()
                try:
                    self._encoder.feed_decoder(data)
                except pylsqpack.DecoderStreamError as exc:
                    raise QpackDecoderStreamError() from exc
                self._decoder_bytes_received += len(data)
            elif stream.stream_type == StreamType.QPACK_ENCODER:
                data = buf.pull_bytes(buf.capacity - buf.tell())
                consumed = buf.tell()
                try:
                    unblocked_streams.update(self._decoder.feed_encoder(data))
                except pylsqpack.EncoderStreamError as exc:
                    raise QpackEncoderStreamError() from exc
                self._encoder_bytes_received += len(data)
            else:
                buf.seek(buf.capacity)
                consumed = buf.tell()

        stream.buffer = stream.buffer[consumed:]
        for stream_id in unblocked_streams:
            stream = self._stream[stream_id]
            http_events.extend(
                self._handle_request_or_push_frame(
                    frame_type=FrameType.HEADERS,
                    frame_data=None,
                    stream=stream,
                    stream_ended=stream.ended and not stream.buffer,
                )
            )
            stream.blocked = False
            stream.blocked_frame_size = None
            if stream.buffer:
                http_events.extend(self._receive_request_or_push_data(stream, b"", stream.ended))
        return http_events

    def _validate_settings(self, settings: dict[int, int]) -> None:
        """Validate received H3 settings."""
        for setting in [Setting.ENABLE_CONNECT_PROTOCOL, Setting.ENABLE_WEBTRANSPORT, Setting.H3_DATAGRAM]:
            if setting in settings and settings[setting] not in (0, 1):
                raise SettingsError(f"{setting.name} setting must be 0 or 1")
        if settings.get(Setting.H3_DATAGRAM) == 1 and self._quic._remote_max_datagram_frame_size is None:
            raise SettingsError("H3_DATAGRAM requires max_datagram_frame_size transport parameter")
        if settings.get(Setting.ENABLE_WEBTRANSPORT) == 1 and settings.get(Setting.H3_DATAGRAM) != 1:
            raise SettingsError("ENABLE_WEBTRANSPORT requires H3_DATAGRAM")
