# Socket-Based Communication Migration Plan

CURRENT PHASE: 4

## Overview

Convert SNYPER from HTTP-based master/target communication to lightweight socket-based messaging. This will eliminate the blocking `urequests` issue while providing faster, more efficient communication with full async support.

## Reference Documentation

**MicroPython Socket Docs**: https://docs.micropython.org/en/latest/library/socket.html

## Critical MicroPython Socket Notes

**IMPORTANT LIMITATIONS & GOTCHAS**:

1. **Address Resolution - CRITICAL**:

   - ❌ **Never use tuple addresses directly** - support varies by port
   - ✅ **Always use `getaddrinfo()`** for portable applications
   - ✅ **Resolve domain names first** before connecting

2. **Platform Differences**:

   - ⚠️ Socket support and constants **vary across MicroPython ports**
   - ⚠️ Not all ports support same socket options/methods
   - 🎯 **Test on actual Pico W hardware** - behavior may differ from development

3. **Error Handling**:

   - ❌ MicroPython raises **`OSError` directly** (not `socket.gaierror`)
   - ⚠️ **Timeout errors are `OSError`** - not specific timeout exceptions
   - 🛡️ **Catch `OSError`** for all socket errors

4. **Timeout Handling**:

   - ❌ **Not every port supports `settimeout()`** method
   - ✅ **Use `select.poll()`** for more portable timeout handling
   - ⚠️ **Async sockets**: Use `uasyncio.wait_for()` for timeouts

5. **Data Transfer**:

   - ❌ **`sendall()` behavior undefined** on non-blocking sockets
   - ✅ **Use `write()` instead** for consistent behavior
   - ✅ **Use `read()` for stream interface** (follows "no short reads" policy)

6. **Stream Interface**:

   - ✅ **Socket objects implement stream interface** directly
   - ⚠️ **`makefile()` is essentially no-op** in MicroPython
   - ❌ **Closing makefile() object closes original socket**

7. **Async Considerations**:
   - ✅ **Use `uasyncio.open_connection()`** instead of raw sockets for async
   - ⚠️ **No explicit async socket support** in base socket module
   - 🎯 **Stick to uasyncio high-level functions** for compatibility

## Current State Analysis

**HTTP Communication Issues**:

- ❌ `urequests.get()` blocks event loop (causing UI freezes)
- ❌ HTTP overhead (headers, parsing, etc.) for simple commands
- ❌ No async HTTP client available for MicroPython
- ❌ Complex error handling for network timeouts

**Socket Communication Benefits**:

- ✅ Native async support with `uasyncio.open_connection()`
- ✅ Lightweight binary or text protocols
- ✅ Direct control over timeouts and error handling
- ✅ Better performance and lower memory usage
- ✅ Eliminates dependency on `urequests` library

## Phase List

- Phase 1: Design Socket Message Protocol
- Phase 2: Implement Master-Side Socket Client
- Phase 3: Implement Target-Side Socket Server
- Phase 4: Replace HTTP Endpoints with Socket Handlers
- Phase 5: Update Registration and Discovery
- Phase 6: Testing and Validation
- Phase 7: Cleanup HTTP Code

## Phase 1: Design Socket Message Protocol

**Goal**: Define simple, efficient message format for master/target communication
**Risk Level**: Low
**Status**: COMPLETE ✅

**Message Format Options**:

**Option A - JSON Lines Protocol**:

```
{"type": "ping", "id": "req_123"}\n
{"type": "pong", "id": "req_123", "status": "alive"}\n
```

**Option B - Binary Protocol**:

```
[1-byte type][2-byte length][payload]
```

**Option C - Simple Text Protocol**:

```
PING:req_123\n
PONG:req_123:alive\n
```

**Message Types**:

- `PING` / `PONG` - Health checks
- `STAND_UP` / `STANDING` - Target stand up command
- `LAY_DOWN` / `DOWN` - Target lay down command
- `ACTIVATE` / `ACTIVATED` - Target activation
- `REGISTER` / `REGISTERED` - Target registration
- `ERROR` - Error responses

**Deliverables**:

- ✅ Protocol specification document (in `socket_protocol.py`)
- ✅ Message parsing/encoding utilities (`SocketMessage`, `MessageLineParser`)
- ✅ Error handling strategy (JSON parsing errors, message validation)

**Implementation**:

- **Chosen Format**: JSON Lines Protocol for human readability and MicroPython compatibility
- **Created**: `src/utils/socket_protocol.py` with complete message handling
- **Tested**: Full test suite validates all message types and parsing
- **Ready**: Protocol ready for Phase 2 implementation

## Phase 2: Implement Master-Side Socket Communication

**Goal**: Add socket communication capabilities to existing master server
**Risk Level**: Medium
**Status**: COMPLETE ✅

**Implementation**:

- **Modified existing `master_server.py`** instead of creating separate socket_client.py
- **Added socket server alongside HTTP server** for dual-protocol support
- **Integrated socket registration handling** with existing callback system

**Key Changes**:

- Added `start_socket_server()` method to MasterServer class
- Implemented `_handle_socket_client()` for incoming socket connections
- Added `_handle_socket_registration()` for socket-based target registration
- Socket server runs on `port + 1` (8081) alongside HTTP server on port 8080

**Integration Points**:

- Socket registration calls same `on_target_register` callback as HTTP
- Maintains backward compatibility with existing HTTP registration
- Future: Replace `urequests.get()` calls in `master_controller.py` with socket commands

**Error Handling**:

- **All socket errors are `OSError`** (not socket-specific exceptions)
- **Use `uasyncio.wait_for()`** for portable timeout handling
- **Connection timeouts, network errors, invalid responses**
- **Target unreachable scenarios**

**MicroPython Compliance**:

- ✅ **Use `uasyncio.open_connection()`** (not raw sockets)
- ✅ **Use `getaddrinfo()`** for address resolution
- ✅ **Use `writer.write()` and `reader.read()`** for data transfer
- ✅ **Catch `OSError`** for all socket operations

## Phase 3: Implement Target-Side Socket Communication

**Goal**: Replace HTTP communication with socket-only communication
**Risk Level**: Medium
**Status**: PARTIAL ✅ (Registration Only)

**Implementation**:

- **Modified existing `target_server.py`** instead of creating separate socket_server.py
- **Added socket registration method** (no HTTP fallback)
- **Will replace HTTP registration workflow entirely**

**Key Changes**:

- Added `register_with_master_socket()` method to TargetServer class
- Socket registration is the only registration method
- Uses JSON Lines protocol as master socket server
- Socket connection to master on `port + 1` (8081)

**Registration Flow**:

1. Target connects to master socket server on port 8081
2. Sends REGISTER message with target_id
3. Master responds with REGISTERED or ERROR message
4. No fallback - socket registration must succeed

**Integration**:

- Will replace existing `register_with_master()` HTTP method
- Maintains same event queue integration for target commands
- Next: Add socket command handlers to replace HTTP routes entirely

**MicroPython Compliance**:

- ✅ **Use `uasyncio.open_connection()`** for socket connections
- ✅ **Use `reader.read()` and `writer.write()`** for data transfer
- ✅ **Catch `OSError`** for all socket operations
- ✅ **Proper connection cleanup** in finally blocks

## Phase 4: Replace HTTP Endpoints with Socket Handlers

**Goal**: Migrate all HTTP endpoints to socket message handlers
**Risk Level**: Medium
**Status**: Pending

**Migration Map**:

- `GET /ping` → `PING` message
- `GET /stand_up` → `STAND_UP` message
- `GET /lay_down` → `LAY_DOWN` message
- `POST /activate` → `ACTIVATE` message with JSON payload
- `POST /register` → `REGISTER` message

**Response Mapping**:

- HTTP status codes → message status fields
- JSON responses → message payloads
- Error responses → `ERROR` message type

## Phase 5: Complete HTTP Removal

**Goal**: Remove all HTTP communication, socket-only system
**Risk Level**: Medium
**Status**: PENDING

**Implementation**:

- **Socket-only registration** (no HTTP fallback)
- **Remove HTTP server from target entirely**
- **Remove HTTP client from master entirely**

**Approach**: Complete HTTP elimination

- Targets use only socket registration to master:8081
- Master only accepts socket registrations
- Remove all HTTP dependencies (`urequests`, `microdot` on targets)
- Master may keep minimal HTTP server for web interface (optional)

**Breaking Changes**:

- Old HTTP-based targets will not work
- All targets must support socket communication
- No gradual migration - clean break from HTTP

## Phase 6: Testing and Validation

**Goal**: Ensure socket communication works correctly
**Risk Level**: Low
**Status**: Pending

**Test Cases**:

- Basic ping/pong communication
- Command execution (stand up, lay down)
- Error handling (network failures, timeouts)
- UI responsiveness during socket operations
- Multiple target handling
- Connection recovery

**Performance Testing**:

- Latency comparison vs HTTP
- Memory usage comparison
- Concurrent connection handling

## Phase 7: Final HTTP Cleanup

**Goal**: Remove all remaining HTTP code from targets
**Risk Level**: Low
**Status**: Pending

**Cleanup Tasks**:

- Remove `urequests` imports and usage from targets
- Remove `microdot` HTTP server from targets
- Remove HTTP routes (`/ping`, `/stand_up`, etc.) from targets
- Remove HTTP-specific error handling
- Clean up debug screen messages
- Remove test delays from target server
- Update documentation to reflect socket-only architecture

## Benefits Summary

**Performance**:

- ⚡ Faster communication (no HTTP overhead)
- 💾 Lower memory usage
- 🔄 Better connection reuse

**Reliability**:

- 🚫 No more blocking `urequests` calls
- ⏱️ Better timeout control
- 🔄 Native async support
- 💥 Fast failure - no graceful degradation

**Maintainability**:

- 🧹 Simpler codebase (no dual protocols)
- 🎯 Purpose-built protocol
- 🔧 Easier debugging
- 🗑️ Eliminates HTTP dependencies

## Implementation Strategy

**Clean Break**: Remove HTTP entirely, socket-only communication
**No Fallbacks**: Systems must work with sockets or fail completely
**Text Protocol**: JSON Lines for human readability and debugging
**Test-Driven**: Validate each phase before proceeding

This migration will solve the UI blocking issue while providing a cleaner, socket-only communication architecture for SNYPER.
