package com.metrolist.shared.db.entities

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "history_snapshot",
    foreignKeys = [ForeignKey(entity = Event::class, parentColumns = ["id"], childColumns = ["eventId"], onDelete = ForeignKey.CASCADE)],
    indices = [Index("eventId", unique = true), Index("remoteFeedbackToken")],
)
data class HistorySnapshot(
    @PrimaryKey val eventId: Long,
    val title: String,
    val artists: String,
    val album: String?,
    val duration: Long?,
    val thumbnailUrl: String?,
    val remoteFeedbackToken: String? = null,
    val artistNamesJson: String? = null,
    val albumId: String? = null,
)

@Entity(
    tableName = "history_provenance",
    primaryKeys = ["source", "legacyId"],
    foreignKeys = [ForeignKey(entity = Event::class, parentColumns = ["id"], childColumns = ["eventId"], onDelete = ForeignKey.SET_NULL)],
    indices = [Index("eventId"), Index("legacyId", "songId")],
)
data class HistoryProvenance(
    val source: String,
    val legacyId: Long,
    val songId: String,
    val playedAt: Long,
    val remoteFeedbackToken: String?,
    val eventId: Long?,
)

@Entity(tableName = "history_import_policy")
data class HistoryImportPolicy(
    @PrimaryKey val id: Int = 1,
    val enabled: Boolean = true,
)
