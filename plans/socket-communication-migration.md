# Socket-Based Communication Migration Plan

CURRENT PHASE: 2

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

## Phase 2: Implement Master-Side Socket Client

**Goal**: Create async socket client to replace HTTP requests
**Risk Level**: Medium
**Status**: Pending

**Implementation**:
```python
# New: src/master/socket_client.py
class MasterSocketClient:
    async def ping_target(self, ip, port=8080):
        reader, writer = await uasyncio.open_connection(ip, port)
        # Send ping message
        # Await response with timeout
        # Parse and return result
    
    async def send_command(self, ip, command, data=None):
        # Generic command sender
        pass
```

**Integration Points**:
- Replace `urequests.get()` calls in `master_controller.py`
- Maintain same method signatures (`ping_targets()`, `raise_all()`, etc.)
- Add connection pooling/reuse if needed

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

## Phase 3: Implement Target-Side Socket Server

**Goal**: Replace HTTP server with lightweight socket server
**Risk Level**: Medium
**Status**: Pending

**Implementation**:
```python
# New: src/target/socket_server.py
class TargetSocketServer:
    async def start_server(self, host='0.0.0.0', port=8080):
        server = await uasyncio.start_server(
            self.handle_client, host, port)
        
    async def handle_client(self, reader, writer):
        # Read message using reader.read()
        # Parse command with MessageLineParser
        # Execute action via event queue
        # Send response using writer.write()
        # Handle OSError for all socket operations
```

**MicroPython Compliance**:
- ✅ **Use `uasyncio.start_server()`** for server creation
- ✅ **Use `reader.read()` and `writer.write()`** for data transfer
- ✅ **Catch `OSError`** for all socket operations
- ✅ **Proper connection cleanup** in finally blocks

**Command Handlers**:
- Ping handler (instant response)
- Stand up handler (queue event)
- Lay down handler (queue event)
- Activate handler (queue event with duration)

**Integration**:
- Replace `target_server.py` HTTP routes
- Maintain same event queue integration
- Keep registration functionality

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

## Phase 5: Update Registration and Discovery

**Goal**: Adapt target registration for socket communication
**Risk Level**: Medium
**Status**: Pending

**Challenges**:
- Master still needs HTTP server for initial registration
- Or implement socket-based registration discovery
- Target discovery and IP tracking

**Options**:
- **Option A**: Keep HTTP for registration, sockets for commands
- **Option B**: Implement UDP broadcast for discovery
- **Option C**: Manual configuration of target IPs

**Recommended**: Option A for simplicity

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

## Phase 7: Cleanup HTTP Code

**Goal**: Remove obsolete HTTP client code
**Risk Level**: Low
**Status**: Pending

**Cleanup Tasks**:
- Remove `urequests` imports and usage
- Remove HTTP-specific error handling
- Clean up debug screen messages
- Update documentation
- Remove test delays from target server

## Benefits Summary

**Performance**:
- ⚡ Faster communication (no HTTP overhead)
- 💾 Lower memory usage
- 🔄 Better connection reuse

**Reliability**:
- 🚫 No more blocking `urequests` calls
- ⏱️ Better timeout control
- 🔄 Native async support

**Maintainability**:
- 🧹 Simpler codebase
- 🎯 Purpose-built protocol
- 🔧 Easier debugging

## Implementation Strategy

**Start Simple**: Begin with text-based protocol for easy debugging
**Incremental**: Migrate one endpoint at a time
**Backward Compatible**: Keep HTTP running until socket version works
**Test-Driven**: Validate each phase before proceeding

This migration will solve the UI blocking issue while providing a cleaner, more efficient communication architecture for SNYPER.