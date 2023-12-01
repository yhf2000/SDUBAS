from pydantic import BaseModel, ConfigDict


class file_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    size: int
    hash_md5: str
    hash_sha256: str
    is_save: int = 0
    time: int = None
    type: int = 0
    server_id : int = None


class user_file_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    file_id: int
    user_id: int


class user_file_all_interface(user_file_interface):
    name: str
    type: str


class RSA_interface(BaseModel):
    user_id: int
    private_key_pem: bytes
    public_key_pem: bytes


class AES_interface(BaseModel):
    file_id: int
    aes_key: str
