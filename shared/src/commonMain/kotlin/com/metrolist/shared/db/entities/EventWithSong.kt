/**
 * Metrolist Project (C) 2026
 * Licensed under GPL-3.0 | See git history for contributors
 */

package com.metrolist.shared.db.entities

import androidx.room.Embedded
import androidx.room.Relation

data class EventWithSong(
    @Embedded
    val event: Event,
    @Relation(
        entity = SongEntity::class,
        parentColumns = ["songId"],
        entityColumns = ["id"],
    )
    val song: Song,
    @Relation(parentColumns = ["id"], entityColumns = ["eventId"])
    val snapshot: HistorySnapshot? = null,
)
