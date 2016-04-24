States = {
    0: 'nostate',
    1: 'running',
    2: 'blocked',
    3: 'paused',
    4: 'shutdown',
    5: 'shutoff',
    6: 'crashed',
    7: 'pmsuspended',
    8: 'last'
}

Reasons = dict(
    running={
        0: 'unknown',
        1: 'booted',
        2: 'migrated',
        3: 'restored',
        4: 'from_snapshot',
        5: 'unpaused',
        6: 'migration_canceled',
        7: 'save_canceled',
        8: 'wakeup',
        9: 'crashed',
        10: 'last'
    },
    blocked={
        0: 'unknown',
        1: 'last'
    },
    crashed={
        0: 'unknown',
        1: 'panicked',
        2: 'last'
    },
    nostate={
        0: 'unknown',
        1: 'last'
    },
    pmsuspended={
        0: 'unknown',
        1: 'last'
    },
    paused={
        0: 'unknown',
        1: 'user',
        2: 'migration',
        3: 'save',
        4: 'dump',
        5: 'ioerror',
        6: 'watchdog',
        7: 'from_snapshot',
        8: 'shutting_down',
        9: 'snapshot',
        10: 'crashed',
        11: 'last'
    },
    shutdown={
        0: 'unknown',
        1: 'user',
        2: 'last'
    },
    shutoff={
        0: 'unknown',
        1: 'shutdown',
        2: 'destroyed',
        3: 'crashed',
        4: 'migrated',
        5: 'saved',
        6: 'failed',
        7: 'from_snapshot',
        8: 'last'
    }
)
