from transmissionrpc import Client


class TransmissionRPC(Client):
    """
    TransmissionRPC class that extends Client.
    """
    def add_torrent(self, torrent, timeout=None, **kwargs):
        return self.get_torrent(super(TransmissionRPC, self).add_torrent(torrent, timeout, **kwargs).id)


transmission = TransmissionRPC('transmission', user='admin', password='admin', port=9091)
