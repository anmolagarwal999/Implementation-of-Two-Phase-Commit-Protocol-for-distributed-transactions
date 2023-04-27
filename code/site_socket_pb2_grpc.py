# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import site_socket_pb2 as site__socket__pb2


class SiteSocketStub(object):
    """Interface exported by the server.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ping_site = channel.unary_unary(
            '/site_socket.SiteSocket/ping_site',
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=site__socket__pb2.BoolMessage.FromString,
        )
        self.BeginTxn = channel.unary_unary(
            '/site_socket.SiteSocket/BeginTxn',
            request_serializer=site__socket__pb2.TxnLocalDetails.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
        self.PrepareTxn = channel.unary_unary(
            '/site_socket.SiteSocket/PrepareTxn',
            request_serializer=site__socket__pb2.TxnIDMessage.SerializeToString,
            response_deserializer=site__socket__pb2.BoolMessage.FromString,
        )
        self.SendGlobalVerdict = channel.unary_unary(
            '/site_socket.SiteSocket/SendGlobalVerdict',
            request_serializer=site__socket__pb2.GlobalVerdictMessage.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
        self.communicate_leader_decision = channel.unary_unary(
            '/site_socket.SiteSocket/communicate_leader_decision',
            request_serializer=site__socket__pb2.GlobalVerdictMessage.SerializeToString,
            response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
        self.fetch_local_decision = channel.unary_unary(
            '/site_socket.SiteSocket/fetch_local_decision',
            request_serializer=site__socket__pb2.TxnIDMessage.SerializeToString,
            response_deserializer=site__socket__pb2.VerdictMessage.FromString,
        )
        self.fetch_txn_exit_stat = channel.unary_unary(
            '/site_socket.SiteSocket/fetch_txn_exit_stat',
            request_serializer=site__socket__pb2.TxnIDMessage.SerializeToString,
            response_deserializer=site__socket__pb2.BoolMessage.FromString,
        )


class SiteSocketServicer(object):
    """Interface exported by the server.
    """

    def ping_site(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def BeginTxn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PrepareTxn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendGlobalVerdict(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def communicate_leader_decision(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def fetch_local_decision(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def fetch_txn_exit_stat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SiteSocketServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'ping_site': grpc.unary_unary_rpc_method_handler(
            servicer.ping_site,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=site__socket__pb2.BoolMessage.SerializeToString,
        ),
        'BeginTxn': grpc.unary_unary_rpc_method_handler(
            servicer.BeginTxn,
            request_deserializer=site__socket__pb2.TxnLocalDetails.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        'PrepareTxn': grpc.unary_unary_rpc_method_handler(
            servicer.PrepareTxn,
            request_deserializer=site__socket__pb2.TxnIDMessage.FromString,
            response_serializer=site__socket__pb2.BoolMessage.SerializeToString,
        ),
        'SendGlobalVerdict': grpc.unary_unary_rpc_method_handler(
            servicer.SendGlobalVerdict,
            request_deserializer=site__socket__pb2.GlobalVerdictMessage.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        'communicate_leader_decision': grpc.unary_unary_rpc_method_handler(
            servicer.communicate_leader_decision,
            request_deserializer=site__socket__pb2.GlobalVerdictMessage.FromString,
            response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        ),
        'fetch_local_decision': grpc.unary_unary_rpc_method_handler(
            servicer.fetch_local_decision,
            request_deserializer=site__socket__pb2.TxnIDMessage.FromString,
            response_serializer=site__socket__pb2.VerdictMessage.SerializeToString,
        ),
        'fetch_txn_exit_stat': grpc.unary_unary_rpc_method_handler(
            servicer.fetch_txn_exit_stat,
            request_deserializer=site__socket__pb2.TxnIDMessage.FromString,
            response_serializer=site__socket__pb2.BoolMessage.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'site_socket.SiteSocket', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

 # This class is part of an EXPERIMENTAL API.


class SiteSocket(object):
    """Interface exported by the server.
    """

    @staticmethod
    def ping_site(request,
                  target,
                  options=(),
                  channel_credentials=None,
                  call_credentials=None,
                  insecure=False,
                  compression=None,
                  wait_for_ready=None,
                  timeout=None,
                  metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/ping_site',
                                             google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                                             site__socket__pb2.BoolMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def BeginTxn(request,
                 target,
                 options=(),
                 channel_credentials=None,
                 call_credentials=None,
                 insecure=False,
                 compression=None,
                 wait_for_ready=None,
                 timeout=None,
                 metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/BeginTxn',
                                             site__socket__pb2.TxnLocalDetails.SerializeToString,
                                             google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PrepareTxn(request,
                   target,
                   options=(),
                   channel_credentials=None,
                   call_credentials=None,
                   insecure=False,
                   compression=None,
                   wait_for_ready=None,
                   timeout=None,
                   metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/PrepareTxn',
                                             site__socket__pb2.TxnIDMessage.SerializeToString,
                                             site__socket__pb2.BoolMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendGlobalVerdict(request,
                          target,
                          options=(),
                          channel_credentials=None,
                          call_credentials=None,
                          insecure=False,
                          compression=None,
                          wait_for_ready=None,
                          timeout=None,
                          metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/SendGlobalVerdict',
                                             site__socket__pb2.GlobalVerdictMessage.SerializeToString,
                                             google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def communicate_leader_decision(request,
                                    target,
                                    options=(),
                                    channel_credentials=None,
                                    call_credentials=None,
                                    insecure=False,
                                    compression=None,
                                    wait_for_ready=None,
                                    timeout=None,
                                    metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/communicate_leader_decision',
                                             site__socket__pb2.GlobalVerdictMessage.SerializeToString,
                                             google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def fetch_local_decision(request,
                             target,
                             options=(),
                             channel_credentials=None,
                             call_credentials=None,
                             insecure=False,
                             compression=None,
                             wait_for_ready=None,
                             timeout=None,
                             metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/fetch_local_decision',
                                             site__socket__pb2.TxnIDMessage.SerializeToString,
                                             site__socket__pb2.VerdictMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def fetch_txn_exit_stat(request,
                            target,
                            options=(),
                            channel_credentials=None,
                            call_credentials=None,
                            insecure=False,
                            compression=None,
                            wait_for_ready=None,
                            timeout=None,
                            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.SiteSocket/fetch_txn_exit_stat',
                                             site__socket__pb2.TxnIDMessage.SerializeToString,
                                             site__socket__pb2.BoolMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class CoordinatorSocketStub(object):
    """Interface exported by the server.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ping_coordinator = channel.unary_unary(
            '/site_socket.CoordinatorSocket/ping_coordinator',
            request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            response_deserializer=site__socket__pb2.BoolMessage.FromString,
        )
        self.perform_transaction = channel.unary_unary(
            '/site_socket.CoordinatorSocket/perform_transaction',
            request_serializer=site__socket__pb2.TxnGlobalMessage.SerializeToString,
            response_deserializer=site__socket__pb2.BoolMessage.FromString,
        )
        self.respond_to_recovering_client = channel.unary_unary(
            '/site_socket.CoordinatorSocket/respond_to_recovering_client',
            request_serializer=site__socket__pb2.TxnIDMessage.SerializeToString,
            response_deserializer=site__socket__pb2.BoolMessage.FromString,
        )


class CoordinatorSocketServicer(object):
    """Interface exported by the server.
    """

    def ping_coordinator(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def perform_transaction(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def respond_to_recovering_client(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CoordinatorSocketServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'ping_coordinator': grpc.unary_unary_rpc_method_handler(
            servicer.ping_coordinator,
            request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            response_serializer=site__socket__pb2.BoolMessage.SerializeToString,
        ),
        'perform_transaction': grpc.unary_unary_rpc_method_handler(
            servicer.perform_transaction,
            request_deserializer=site__socket__pb2.TxnGlobalMessage.FromString,
            response_serializer=site__socket__pb2.BoolMessage.SerializeToString,
        ),
        'respond_to_recovering_client': grpc.unary_unary_rpc_method_handler(
            servicer.respond_to_recovering_client,
            request_deserializer=site__socket__pb2.TxnIDMessage.FromString,
            response_serializer=site__socket__pb2.BoolMessage.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'site_socket.CoordinatorSocket', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))

 # This class is part of an EXPERIMENTAL API.


class CoordinatorSocket(object):
    """Interface exported by the server.
    """

    @staticmethod
    def ping_coordinator(request,
                         target,
                         options=(),
                         channel_credentials=None,
                         call_credentials=None,
                         insecure=False,
                         compression=None,
                         wait_for_ready=None,
                         timeout=None,
                         metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.CoordinatorSocket/ping_coordinator',
                                             google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                                             site__socket__pb2.BoolMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def perform_transaction(request,
                            target,
                            options=(),
                            channel_credentials=None,
                            call_credentials=None,
                            insecure=False,
                            compression=None,
                            wait_for_ready=None,
                            timeout=None,
                            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.CoordinatorSocket/perform_transaction',
                                             site__socket__pb2.TxnGlobalMessage.SerializeToString,
                                             site__socket__pb2.BoolMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def respond_to_recovering_client(request,
                                     target,
                                     options=(),
                                     channel_credentials=None,
                                     call_credentials=None,
                                     insecure=False,
                                     compression=None,
                                     wait_for_ready=None,
                                     timeout=None,
                                     metadata=None):
        return grpc.experimental.unary_unary(request, target, '/site_socket.CoordinatorSocket/respond_to_recovering_client',
                                             site__socket__pb2.TxnIDMessage.SerializeToString,
                                             site__socket__pb2.BoolMessage.FromString,
                                             options, channel_credentials,
                                             insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
