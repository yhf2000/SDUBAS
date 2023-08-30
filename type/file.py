from pydantic import BaseModel, ConfigDict


class file_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    size: int
    hash_md5: str
    hash_sha256: str


class user_file_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    file_id: int = None
    user_id: int = None
