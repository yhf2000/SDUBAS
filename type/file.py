from pydantic import BaseModel, ConfigDict


class file_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    size: int
    hash_md5: str
    hash_sha256: str
    has_delete: int = 0
    is_save: int = 0
    time: int = None


class user_file_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    file_id: int
    user_id: int
    has_delete: int = 0
    video_time: int = None


class user_file_all_interface(user_file_interface):
    name: str
    type: str


class RSA_interface(BaseModel):
    user_id: int
    private_key_pem: bytes
    public_key_pem: bytes
