#═══════════════════════════════════════════════════════════════

"""Generated protocol buffer code — TANBIR YT Edition."""

# ─── Import thư viện Protobuf Core ───
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)


# ═══════════════════════════════════════════════════════════════
#              ★ Khởi tạo Symbol Database ★
# ═══════════════════════════════════════════════════════════════

_sym_db = _symbol_database.Default()


# ═══════════════════════════════════════════════════════════════
# #        ★ Định nghĩa Descriptor (RemoveFriend ) ★
# ═══════════════════════════════════════════════════════════════
#
#  Cấu trúc thông điệp (Message Structure) :
#  ┌─────────────────────────────────────────┐
#  │  RemoveFriend                           │
#  ├─────────────────────────────────────────┤
#  │  AuthorUid  : int64  (field 1)          │
#  │  TargetUid  : int64  (field 2)          │
#  └─────────────────────────────────────────┘
#
#  AuthorUid → UID người thực hiện xoá bạn
#  TargetUid → UID bạn bè bị xoá
# ═══════════════════════════════════════════════════════════════

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x16RemoveFriend_Req.proto'
    b'\"4\n\x0cRemoveFriend'
    b'\x12\x11\n\tAuthorUid\x18\x01 \x01(\x03'
    b'\x12\x11\n\tTargetUid\x18\x02 \x01(\x03'
    b'b\x06proto3'
)


# ═══════════════════════════════════════════════════════════════
#              ★ Bộ dựng Message và Enum (TANBIR YT) ★
# ═══════════════════════════════════════════════════════════════

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'RemoveFriend_Req_pb2', _globals)


# ═══════════════════════════════════════════════════════════════
#              ★ Kiểm tra hỗ trợ C-Descriptor ★
# ═══════════════════════════════════════════════════════════════

if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None

    # RemoveFriend Thiết lập phạm vi serialized của message
    _globals['_REMOVEFRIEND']._serialized_start = 26
    _globals['_REMOVEFRIEND']._serialized_end   = 78


# @@protoc_insertion_point(module_scope)


# ═══════════════════════════════════════════════════════════════
#                    ★ TANBIR YT — END OF FILE ★
# ═══════════════════════════════════════════════════════════════
