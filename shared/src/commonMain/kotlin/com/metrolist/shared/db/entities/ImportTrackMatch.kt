package com.metrolist.shared.db.entities

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index

@Entity(
    tableName = "import_track_match",
    primaryKeys = ["playlistId", "provider", "trackKey"],
    foreignKeys = [
        ForeignKey(PlaylistEntity::class, ["id"], ["playlistId"], onDelete = ForeignKey.CASCADE),
        ForeignKey(SongEntity::class, ["id"], ["songId"], onDelete = ForeignKey.CASCADE),
    ],
    indices = [Index("songId")],
)
data class ImportTrackMatch(
    val playlistId: String,
    val provider: String,
    val trackKey: String,
    val songId: String,
)
