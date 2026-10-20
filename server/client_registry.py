import threading


class ClientRegistry():
    def __init__(self):
        self._clients = {}
        self._lock = threading.Lock()

    #מוסיפה לקוח. מחזירה אמת  אם הצליחה, שקר אם השרת מלא
    def add(self, client_id, handler, max_clients) -> bool:
        with self._lock:
            if len(self._clients) >= max_clients:
                return False
            else:

                self._clients[client_id] = handler
                return True
    #מוחקת לקוח. אם הוא כבר לא שם, לא קורה כלום
    def remove(self, client_id):
        with self._lock:
            self._clients.pop(client_id, None)

    #מחזירה עותק של רשימת ה־handlers
    def snapshot(self) ->list:
        with self._lock:
            return list(self._clients.values())

    def count(self) -> int:
        with self._lock:
            return len(self._clients)