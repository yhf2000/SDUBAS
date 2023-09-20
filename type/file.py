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
    file_id: int = None
    user_id: int = None
    has_delete: int = 0
    video_time: int = None
