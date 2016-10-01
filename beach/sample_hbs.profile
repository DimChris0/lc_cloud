rList().addSequence( _.hbs.CONFIGURATION,
                     rSequence().addInt32( _.hbs.CONFIGURATION_ID, HbsCollectorId.EXFIL )
                                .addList( _.hbs.LIST_NOTIFICATIONS, rList().addInt32( _.hbs.NOTIFICATION_ID, _.notification.NEW_PROCESS )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.TERMINATE_PROCESS )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.CODE_IDENTITY )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.NEW_TCP4_CONNECTION )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.NEW_UDP4_CONNECTION )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MODULE_LOAD )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.DNS_REQUEST )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.HIDDEN_MODULE_DETECTED )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_CREATE )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_DELETE )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.NETWORK_SUMMARY )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_GET_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_DEL_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_MOV_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_HASH_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_INFO_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.DIR_LIST_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MEM_MAP_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MEM_READ_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MEM_HANDLES_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MEM_FIND_HANDLE_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MEM_STRINGS_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MEM_FIND_STRING_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.OS_SERVICES_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.OS_DRIVERS_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.OS_KILL_PROCESS_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.OS_PROCESSES_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.OS_AUTORUNS_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.EXEC_OOB )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.GET_EXFIL_EVENT_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.MODULE_MEM_DISK_MISMATCH )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.YARA_DETECTION )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.SERVICE_CHANGE )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.DRIVER_CHANGE )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.AUTORUN_CHANGE )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.FILE_MODIFIED )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.NEW_DOCUMENT )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.GET_DOCUMENT_REP )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.VOLUME_MOUNT )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.VOLUME_UNMOUNT )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.RECON_BURST )
                                                                           .addInt32( _.hbs.NOTIFICATION_ID, _.notification.POSSIBLE_DOC_EXPLOIT ) ) )
       .addSequence( _.hbs.CONFIGURATION,
                     rSequence().addInt32( _.hbs.CONFIGURATION_ID, HbsCollectorId.OS_FORENSIC )
                                .addTimedelta( _.base.TIMEDELTA, ( 60 * 60 * 24 * 1 ) ) )
       .addSequence( _.hbs.CONFIGURATION,
                     rSequence().addInt32( _.hbs.CONFIGURATION_ID, HbsCollectorId.DOC_COLLECTOR )
                                .addList( _.base.EXTENSIONS, rList().addStringA( _.base.EXTENSION, ".bat" )
                                                                    .addStringA( _.base.EXTENSION, ".js" )
                                                                    .addStringA( _.base.EXTENSION, ".ps1" )
                                                                    .addStringA( _.base.EXTENSION, ".sh" )
                                                                    .addStringA( _.base.EXTENSION, ".py" )
                                                                    .addStringA( _.base.EXTENSION, ".pdf" )
                                                                    .addStringA( _.base.EXTENSION, ".doc" )
                                                                    .addStringA( _.base.EXTENSION, ".vbs" )
                                                                    .addStringA( _.base.EXTENSION, ".rtf" ) )
                                .addList( _.base.PATTERNS, rList().addStringA( _.base.STRING_PATTERN, "/tmp/" )
                                                                  .addStringA( _.base.STRING_PATTERN, "\\temp\\" ) ) )