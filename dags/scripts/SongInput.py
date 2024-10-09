from pydantic import BaseModel

class SongInput(BaseModel):
    song_name: str
