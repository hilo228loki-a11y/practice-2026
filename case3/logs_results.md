# Результаты анализа логов (2026-11-16)

Обработано вложенных архивов: 922 из 926; пропущено (больше 120 МБ или не открылись): 4
- пропущен архив размером 126 МБ
- пропущен архив размером 614 МБ
- пропущен архив размером 614 МБ
- пропущен архив размером 614 МБ

## Общая картина
- архивов с ошибками «connection was refused» в журнале VPN: 78.9 %
- архивов со стек-трейсами приложения: 99.1 %
- архивов со строками ошибок [E]/Exception в журнале приложения: 99.5 %
- архивов с заблокированными соединениями (-> block): 86.8 %

## Ошибки по платформе
| группа | архивов | % с connection refused | % со стек-трейсами | % с ошибками [E] |
|---|---|---|---|---|
| android | 872 | 80.5 | 99.5 | 99.7 |
| windows | 22 | 40.9 | 95.5 | 95.5 |
| androidTv | 11 | 9.1 | 81.8 | 90.9 |
| macOs | 10 | 90.0 | 100.0 | 100.0 |
| ios | 6 | 100.0 | 83.3 | 100.0 |

## Ошибки по версии ОС (основная версия)
| группа | архивов | % с connection refused | % со стек-трейсами | % с ошибками [E] |
|---|---|---|---|---|
| android 16 | 224 | 78.6 | 99.6 | 99.6 |
| android 15 | 155 | 87.7 | 100.0 | 100.0 |
| android 13 | 155 | 87.1 | 100.0 | 100.0 |
| android 14 | 121 | 81.0 | 100.0 | 100.0 |
| android 12 | 74 | 74.3 | 98.6 | 98.6 |
| android 11 | 67 | 73.1 | 100.0 | 100.0 |
| android 10 | 62 | 74.2 | 96.8 | 98.4 |
| windows Windows 10 Pro | 14 | 50.0 | 100.0 | 100.0 |
| android 9 | 8 | 62.5 | 100.0 | 100.0 |
| androidTv 11 | 7 | 14.3 | 71.4 | 85.7 |
| macOs Version 26 | 6 | 83.3 | 100.0 | 100.0 |
| android 8 | 5 | 40.0 | 100.0 | 100.0 |

## Ошибки по версии приложения
| группа | архивов | % с connection refused | % со стек-трейсами | % с ошибками [E] |
|---|---|---|---|---|
| 2026.9.9 | 459 | 61.9 | 98.5 | 99.1 |
| 2026.7.16 | 177 | 94.4 | 100.0 | 100.0 |
| 2026.8.19 | 111 | 96.4 | 100.0 | 100.0 |
| 2026.7.7 | 81 | 100.0 | 100.0 | 100.0 |
| 2026.5.14 | 25 | 96.0 | 100.0 | 100.0 |
| 2026.6.11 | 16 | 100.0 | 100.0 | 100.0 |
| 2026.6.5 | 12 | 100.0 | 100.0 | 100.0 |
| 2026.4.15 | 7 | 71.4 | 100.0 | 100.0 |
| 2025.11.20 | 5 | 100.0 | 100.0 | 100.0 |
| 2026.3.10 | 5 | 100.0 | 100.0 | 100.0 |

## Самые частые строки ошибок приложения (числа заменены на <n>)
- 1,140,618 × Network exception
- 1,134,626 × Network Exception
- 949,748 × ErrorType: DioExceptionType.connectionError
- 234,253 × connect failed: <tok>: SocketException: Failed host lookup: 'api.pipster.win' (OS Error: No address associated with hostname, errno = <n>)
- 223,115 × Handshake failed: <tok>: SocketException: Failed host lookup: 'api.pipster.win' (OS Error: No address associated with hostname, errno = <n>)
- 222,801 × Error: SocketException: Failed host lookup: 'api.pipster.win' (OS Error: No address associated with hostname, errno = <n>)
- 222,468 × WS token sync REST call failed (null): DioException [connection error]: The connection errored: Failed host lookup: 'api.pipster.win' This i
- 142,337 × ErrorType: DioExceptionType.connectionTimeout
- 142,337 × Error message: The request connection took longer than <n>:<n>:<n>.<n> and it was aborted. To get rid of this exception, try raising the Req
- 72,737 × Global notification topic subscribe failed (attempt <n>): TimeoutException after <n>:<n>:<n>.<n>: Future not completed. Next retry in <n>s.
- 41,788 × In order to resolve this exception you typically have either to verify and fix your request code or you have to fix the server code.
- 29,712 × connect failed: TimeoutException after <n>:<n>:<n>.<n>: Future not completed
- 25,556 × Handshake failed: TimeoutException after <n>:<n>:<n>.<n>: Future not completed
- 25,342 × ErrorType: DioExceptionType.badResponse
- 25,342 × Error message: This exception was thrown because the response has a status code of <n> and RequestOptions.validateStatus was configured to t
- 23,191 × ErrorType: DioExceptionType.unknown
- 23,059 × WS token sync REST call failed (null): DioException [connection timeout]: The request connection took longer than <n>:<n>:<n>.<n> and it was
- 22,537 × Skipped before start: error type=DioExceptionType.badResponse, inner=null
- 14,686 × connect failed: <tok>: WebSocketException: Connection to 'https://api.pipster.win:<n>/api/v<n>/notifications/ws#' was not upgraded to websoc
- 12,752 × Cloud messaging init timed out: TimeoutException after <n>:<n>:<n>.<n>: Cloud messaging initialize exceeded <n>:<n>:<n>.<n>. Push notificati

## Самые частые ошибки VPN-ядра
- 1,764,338 × [Debug] [<n>] proxy: Xtls Unpadding new block, content <n> padding <n> command <n>
- 984,542 × [Debug] [<n>] proxy: XtlsPadding <n> <n> <n>
- 846,874 × [Info] [<n>] proxy/tun: processing from udp:<ip>:<n> to udp:<ip>:<n>
- 803,932 × [Info] [<n>] transport/internet/tcp: dialing TCP to tcp:<ip>:<n>
- 790,284 × [Debug] transport/internet/udp: dispatch request to: udp:<ip>:<n>
- 732,633 × [Info] [<n>] proxy/dns: handling DNS traffic to udp:<ip>:<n>
- 731,380 × [Info] [<n>] app/dispatcher: taking detour [dnsOut] for [udp:<ip>:<n>]
- 720,466 × [Info] [<n>] proxy/tun: processing from tcp:<ip>:<n> to tcp:<ip>:<n>
- 583,083 × [Info] transport/internet/udp: establishing new connection for udp:<ip>:<n>
- 583,063 × [Info] app/dispatcher: taking detour [dnsOut] for [udp:<ip>:<n>]
- 583,059 × [Info] proxy/dns: handling DNS traffic to udp:<ip>:<n>
- 527,979 × [Info] [<n>] proxy/vless/outbound: tunneling request to tcp:<ip>:<n> via <ip>:<n>
- 406,864 × [Debug] [<n>] proxy: XtlsFilterTls found tls client hello! <n>
- 367,791 × [Info] transport/internet/tcp: dialing TCP to tcp:<ip>:<n>
- 294,261 × [Debug] [<n>] proxy: CopyRawConn (maybe) readv

## Что обычно происходит перед ошибкой в журнале приложения (предыдущая строка → строка ошибки)
- 949,748 × «Status code: Unknown» → «ErrorType: DioExceptionType.connectionError»
- 791,118 × «Headers: accept: application/json | Content-Type: application/json | X-Request-ID: <uuid> | X-Package-Name: com.vipin.pipster | Accept-Langu» → «Network Exception»
- 791,118 × «Headers: accept: application/json | Content-Type: application/json | X-Request-ID: <uuid> | X-Package-Name: com.vipin.pipster | Accept-Langu» → «Network exception»
- 223,114 × «status update connected=false» → «connect failed: <tok>: SocketException: Failed host lookup: 'api.pipster.win' (OS Error: No address associated with hostname, errno = <n>)»
- 165,301 × «WS handshake headers: {Authorization: Bearer ***}» → «Handshake failed: <tok>: SocketException: Failed host lookup: 'api.pipster.win' (OS Error: No address associated with hostname, errno = <n>)»
- 142,337 × «Status code: Unknown» → «ErrorType: DioExceptionType.connectionTimeout»
- 142,337 × «Status code: Unknown» → «Error message: The request connection took longer than <n>:<n>:<n>.<n> and it was aborted. To get rid of this exception, try raising the Req»
- 57,648 × «Waiting for handshake ready» → «Handshake failed: <tok>: SocketException: Failed host lookup: 'api.pipster.win' (OS Error: No address associated with hostname, errno = <n>)»
- 41,788 × «Read more about status codes at https://developer.mozilla.org/en-US/docs/Web/HTTP/Status» → «In order to resolve this exception you typically have either to verify and fix your request code or you have to fix the server code.»
- 33,337 × «<asynchronous  suspension>» → «Network exception»
- 32,919 × «<asynchronous  suspension>» → «Network Exception»
- 25,556 × «status update connected=false» → «connect failed: TimeoutException after <n>:<n>:<n>.<n>: Future not completed»
- 25,342 × «Status code: <n>» → «ErrorType: DioExceptionType.badResponse»
- 25,342 × «Status code: <n>» → «Error message: This exception was thrown because the response has a status code of <n> and RequestOptions.validateStatus was configured to t»
- 23,191 × «Status code: Unknown» → «ErrorType: DioExceptionType.unknown»
- 18,421 × «WS handshake headers: {Authorization: Bearer ***}» → «Handshake failed: TimeoutException after <n>:<n>:<n>.<n>: Future not completed»
- 13,354 × «client status changed: connected=true manual=false networkTransition=false autoReconnect=true» → «Global notification topic subscribe failed (attempt <n>): TimeoutException after <n>:<n>:<n>.<n>: Future not completed. Next retry in <n>s.»
- 13,237 × «WS handshake headers: {Authorization: Bearer ***}» → «connect failed: <tok>: WebSocketException: Connection to 'https://api.pipster.win:<n>/api/v<n>/notifications/ws#' was not upgraded to websoc»
- 12,848 × «App hidden, stop polling» → «Global notification topic subscribe failed (attempt <n>): TimeoutException after <n>:<n>:<n>.<n>: Future not completed. Next retry in <n>s.»
- 11,503 × «Headers: accept: application/json | Content-Type: application/json | X-Request-ID: <uuid> | X-Package-Name: com.vipin.pipster | Accept-Langu» → «Skipped before start: error type=DioExceptionType.badResponse, inner=null»