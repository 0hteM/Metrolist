package com.metrolist.shared.db.daos

import androidx.room.Dao
import androidx.room.RoomWarnings

@Dao
@Suppress(RoomWarnings.QUERY_MISMATCH)
interface DatabaseDao :
    SongDao,
    PlaylistDao,
    HistoryDao,
    CacheDao
