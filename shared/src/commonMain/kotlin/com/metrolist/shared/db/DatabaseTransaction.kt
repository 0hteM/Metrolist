package com.metrolist.shared.db

import androidx.room.immediateTransaction
import androidx.room.useWriterConnection

suspend fun <R> MusicDatabase.withDatabaseTransaction(block: suspend () -> R): R =
    useWriterConnection { transactor ->
        transactor.immediateTransaction { block() }
    }
