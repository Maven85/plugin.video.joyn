# -*- coding: utf-8 -*-

CONST = {
        'BASE_URL': 'https://www.joyn.de',
        'ENTITLEMENT_URL': 'entitlement-token',
        'IP_API_URL': 'http://ip-api.com/json?lang={:s}&fields=status,country,countryCode',
        'AUTH_URL': 'https://auth.joyn.de/auth',
        'AUTH_ANON': '/anonymous',
        'AUTH_REFRESH': '/refresh',
        'AUTH_LOGIN': '/login',
        'AUTH_LOGOUT': '/logout',
        'SSO_AUTH_URL': 'https://auth.joyn.de/sso/endpoints',
        'OAUTH_URL': 'https://www.joyn.de/oauth',
        'CLIENT_NAMES': ['web', 'ios', 'android'],
        'EDGE_UA': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46',
        'JOYN_CLIENT_VERSION': '5.343.25',
        'MAX_VIDEO_TRIES': 5,
        'SIGNATURE_KEY': 'MzU0MzM3MzgzMzM4MzMzNjM1NDMzNzM4MzYzNDM2MzYzNTQzMz'\
                         'czODM2MzYzMzM4MzIzNjM1NDMzNzM4MzMzMDM2MzQzNTM5MzU0'\
                         'MzM3MzgzMzM5MzMzNTMyMzQzNTQzMzczODM2MzUzMzM5MzU0Mz'\
                         'M3MzgzMzM4MzMzMjMzNDYzNTQzMzczODM2MzYzMzMzMzM0NDMz'\
                         'NDIzNTQzMzczODMzMzgzNjM2MzMzNQ==',

        'PRELOAD_JS_CONFIGS': {
            'API_GW_API_KEY': '"x-api-key":.*?"(.*?)"',
        },
        'CHUNKS_JS_CONFIGS': {
            'PLAYERCONFIG_URL': 'https://playerconfig.*?.json',
        },
        'COUNTRIES': {
            'DE': {
                'language': 'de',
                'setting_id': '1',
            },
        },

        'CACHE_DIR': 'cache',
        'TEMP_DIR': 'tmp',
        'DATA_DIR': 'data',
        'CACHE': {
            'CONFIG': { 'key': 'config', 'expires': 432000 },
            'EPG': { 'key': 'epg', 'expires': 36000 },
            'ETAGS': { 'key': 'etags', 'expires': None},
            'ACCOUNT_INFO': { 'key': 'account_info', 'expires': 36000}
        },

        'CACHE_FILES_KEEP': ['config.json'],

        'ETAGS_TTL': 1209600,  # 14 days

        'LASTSEEN_ITEM_COUNT': 20,
        'UEPG_REFRESH_INTERVAL': 7200,
        'UEPG_ROWCOUNT': 5,
        'INPUTSTREAM_ADDON': 'inputstream.adaptive',

        'MSG_IDS': {
            'ADD_TO_WATCHLIST': 30651,
            'ADD_TO_WATCHLIST_PRX': 30653,
            'REMOVE_FROM_WATCHLIST': 30652,
            'REMOVE_FROM_WATCHLIST_PRFX': 30654,
            'MEDIA_LIBRARY': 30622,
            'CATEGORY': 30623,
            'TV_SHOW': 30624,
            'SEASON': 30625,
            'EPISODE': 30625,
            'WATCHLIST': 30601,
            'MEDIA_LIBRARIES': 30602,
            'CATEGORIES': 30603,
            'SEARCH': 30604,
            'LIVE_TV': 30605,
            'TV_GUIDE': 30606,
            'MEDIA_LIBRARIES_PLOT': 30608,
            'CATEGORIES_PLOT': 30609,
            'WATCHLIST_PLOT': 30607,
            'SEARCH_PLOT': 30610,
            'LIVE_TV_PLOT': 30611,
            'TV_GUIDE_PLOT': 30612,
            'WL_TYPE_ADDED': 30526,
            'WL_TYPE_REMOVED': 30527,
            'MSG_INPUSTREAM_NOT_ENABLED': 30501,
            'MSG_WIDEVINE_NOT_FOUND': 30502,
            'MSG_NO_SEARCH_RESULTS': 30525,
            'MSG_NO_FAVS_YET': 30528,
            'MSG_FAVS_UNAVAILABLE': 30529,
            'ERROR': 30521,
            'MSG_ERR_TRY_AGAIN': 30522,
            'MSG_ERROR_CONFIG_DECRYPTION': 30523,
            'MSG_ERROR_NO_VIDEOSTEAM': 30524,
            'LIVETV_TITLE': 30655,
            'LIVETV_UNTIL': 30656,
            'LIVETV_UNTIL_AND_NEXT': 30657,
            'MIN_AGE': 30658,
            'VIDEO_AVAILABLE': 30650,
            'SEASON_NO': 30621,
            'MSG_CONFIG_VALUES_INCOMPLETE': 30530,
            'MSG_NO_ACCESS_TO_URL': 30531,
            'MSG_COUNTRY_NOT_DETECTED': 30532,
            'MSG_COUNTRY_INVALID': 30533,
            'CANCEL': 30503,
            'OPEN_ADDON_SETTINGS': 30504,
            'CACHE_WAS_CLEARED': 30659,
            'CACHE_COULD_NOT_BE_CLEARED': 30660,
            'LANG_CODE': 30661,
            'MSG_VIDEO_UNAVAILABLE': 30662,
            'MSG_GAPHQL_ERROR': 30663,
            'MSG_NO_CONTENT': 30664,
            'CONTINUE_WATCHING': 30665,
            'RECOMMENDATION': 30666,
            'MOVIE': 30667,
            'SERIES': 30668,
            'TITLE_LABEL': 30669,
            'LOGGED_IN_LABEL': 30670,
            'LOGIN_FAILED_LABEL': 30671,
            'ACCOUNT_INFO_LABEL': 30672,
            'YES_LABEL': 30673,
            'NO_LABEL': 30674,
            'USERNAME_LABEL': 30675,
            'PASSWORD_LABEL': 30676,
            'MSG_INVALID_EMAIL': 30677,
            'LOGOUT_OK_LABEL': 30678,
            'NOT_LOGGED_IN_LABEL': 30679,
            'LOGOUT_NOK_LABEL': 30680,
            'RETRY': 30505,
            'ACCOUNT': 30352,
            'MSG_RERESH_AUTH_FAILED_RELOG': 30534,
            'MSG_RERESH_AUTH_FAILED': 30535,
            'CONTINUE_ANONYMOUS': 30506,
            'JOYN_BOOKMARKS': 30681,
            'JOYN_BOOKMARK_LABEL': 30682,
            'MSG_JOYN_BOOKMARK_ADD_SUCC': 30683,
            'MSG_JOYN_BOOKMARK_ADD_FAIL': 30684,
            'MSG_JOYN_BOOKMARK_DEL_SUCC': 30685,
            'MSG_JOYN_BOOKMARK_DEL_FAIL': 30686,
            'ADD_TO_JOYN_BOOKMARKS_LABEL': 30687,
            'DEL_FROM_JOYN_BOOKMARKS_LABEL': 30688,
            'MPAA_PIN': 30689,
            'MSG_INVALID_MPAA_PIN': 30690,
            'PLUS_HIGHLIGHT_LABEL': 30691,
            'MSG_INVALID_PASSWORD': 30692,
            'NO_INFORMATION_AVAILABLE': 30693,
            'LOGIN_NOW_LABEL': 30694,
            'LOGIN_LABEL': 30136,
            'ASCENDING_LABEL': 30695,
            'DESCENDING_LABEL': 30696,
            'TV_SHOWS': 30697,
            'TV_SHOWS_PLOT': 30698,
            'MOVIES': 30699,
            'MOVIES_PLOT': 30700,
            'SPORT': 30701,
            'SPORT_PLOT': 30702,
        },

        'VIEW_MODES': {
            'Standard': {
                'skin.estuary': '0',
            },
            'List': {
                'skin.estuary': '50',
            },
            'Poster': {
                'skin.estuary': '51',
            },
            'IconWall': {
                'skin.estuary': '52',
            },
            'Shift': {
                'skin.estuary': '53',
             },
            'InfoWall': {
                'skin.estuary': '54',
            },
            'WideList': {
                'skin.estuary': '55',
            },
            'Wall': {
                'skin.estuary': '500',
            },
            'Banner': {
                'skin.estuary': '501',
            },
            'Fanart': {
                'skin.estuary': '502',
            },
        },
        'LICENSE_FILTER': {
            'hasActivePlus': 'FREE',
        },
        'LICENSE_TYPES': {
            'FREE': {
                'AVOD': {
                    'MARKING_TYPES': ['JOYN_ORIGINAL', 'HD', 'PREVIEW']
                }
            },
            'PAID': {
                'SVOD': {
                    'SUBSCRIPTION_TYPE': 'hasActivePlus',
                    'MARKING_TYPES': ['PREMIUM', 'HD', 'JOYN_ORIGINAL', 'PLUS', 'PREVIEW'],
                },
            },
        },
        'FOLDERS': {
            'INDEX': {
                'content_type': 'tags',
                'view_mode': 'categories_view',
            },
             'CATEORIES': {
                'content_type': 'tags',
                'view_mode': 'categories_view',
                'cacheable': True,
            },
            'MEDIA_LIBS': {
                'content_type': 'tags',
                'view_mode': 'categories_view',
                'cacheable': True,
            },
            'WATCHLIST': {
                'content_type': 'videos',
                'view_mode': 'watchlist_view',
            },
            'CATEGORY': {
                'content_type': 'tvshows',
                'view_mode': 'category_view',
                'cacheable': True,
            },
            'LIVE_TV': {
                'content_type': 'videos',
                'view_mode': 'livetv_view',
            },
            'TV_SHOWS': {
                'content_type': 'tvshows',
                'view_mode': 'tvshow_view',
                'cacheable': True,
            },
            'SEASONS': {
                'content_type': 'seasons',
                'view_mode': 'season_view',
                'sort': {
                   'order_type': '7',  # SortByTitle
                   'setting_id': 'season_order',
                },
                'cacheable': True,
            },
            'EPISODES': {
                'content_type': 'episodes',
                'view_mode': 'episode_view',
                'sort': {
                   'order_type': '23',  # SortByEpisodeNumber
                   'setting_id': 'episode_order',
                },
                'cacheable': True,
            },
        },

        'SETTING_VALS': {
            'SORT_ORDER_DEFAULT': '0',
            'SORT_ORDER_ASC': '1',
            'SORT_ORDER_DESC': '2',
        },

        'GRAPHQL': {
            'API_URL': 'https://api.joyn.de/graphql',

            'REQUIRED_HEADERS': ['x-api-key', 'joyn-platform'],

            'STATIC_VARIABLES': {
                'first': 1000,
                'offset': 0,
            },

        'METADATA': {
            'TVCHANNEL': {
                'TEXTS': {'title': 'title'},
                'ART': {
                    'logo': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'thumb': 'profile:original',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                    },
                    'brand': {
                        'logo': {
                            'icon': 'profile:nextgen-web-artlogo-183x75',
                            'thumb': 'profile:original',
                            'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                        },
                    },
                },
            },

            'TVSHOW': {
                'TEXTS': {'title': 'title', 'description': 'plot'},
                'ART': {
                    'primaryImage': {
                        'thumb': 'profile:original'
                    },
                    'artLogoImage': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                        'clearart': 'profile:nextgen-web-artlogo-183x75',
                    },
                    'heroLandscapeImage': {
                        'thumb': 'profile:original',
                        'fanart': 'profile:nextgen-web-herolandscape-1920x',
                        'landscape': 'profile:nextgen-web-herolandscape-1920x',
                    },
                    'heroPortraitImage': {
                        'thumb': 'profile:original',
                        'poster': 'profile:nextgen-webphone-heroportrait-563x',
                    },
                },
            },

           'EPISODE': {
               'TEXTS': {'title': 'title', 'description': 'plot'},
               'ART': {
                    'primaryImage': {
                        'thumb': 'profile:original'
                    },
                    'artLogoImage': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                    },
                    'heroLandscapeImage': {
                        'fanart': 'profile:nextgen-web-herolandscape-1920x',
                    },
                    'heroPortrait': {
                        'poster': 'profile:nextgen-webphone-heroportrait-563x',
                    },
                },
            },

            'EPG': {
                'TEXTS': {'title': 'title', 'secondaryTitle': 'plot'},
                'ART': {
                    'images': {
                        'LIVE_STILL': {
                            'poster': 'profile:original',
                            'thumb': 'profile:original',
                        },
                    },
                },
            },

            'TEASER': {
                'TEXTS': {'title': 'title'},
                'ART': {
                    'images': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'thumb': 'profile:original',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                    },
                },
            },
        },

        'NAVIGATION': {
            'OPERATION': 'Navigation',
            'HASH': '5b179fb89fe131a6f013346033a9c2d675575973c67c4ec55830946439f17845',
        },

        'LANDINGPAGECLIENT': {
            'OPERATION': 'LandingPageClient',
            'REQUIRED_VARIABLES': ['path'],
            'HASH': 'b74048f7eef3787e5d48163a8207a8e26910bb28adb1209cf9601ed48e872236',
        },

       'LANDINGBLOCKS': {
            'OPERATION': 'LandingBlocks',
            'REQUIRED_VARIABLES': ['ids'],
            'BOOKMARKS': True,
            'HASH': '86000cc3d4c43fb1d96fdf1a020558286884b0a91668ec270127517ce5d4c551',
        },

        'CHANNEL': {
            'OPERATION': 'PageDetailMediaLibrary',
            'REQUIRED_VARIABLES': ['path', 'first', 'offset'],
            'BOOKMARKS': True,
            'HASH': '12b0037c038d62ca9f478c46e766c2088c585562797cf47124329e2622835624',
        },

        'COLLECTION': {
            'OPERATION': 'PageCollectionsDetail',
            'REQUIRED_VARIABLES': ['path'],
            'BOOKMARKS': True,
            'HASH': '07f80fcd0758c21bc2c3d326d76c4aa0f04b838444f921c663ec98dca331f6ba',
        },

        'COMPILATION': {
            'OPERATION': 'CompilationDetailPageStatic',
            'REQUIRED_VARIABLES': ['path'],
            'BOOKMARKS': True,
            'HASH': '9984e66e838b47c06ee696822e73afb5abe06239446e072df33065565635d778',
        },

        'MOVIES': {
            'OPERATION': 'PageMovieDetailStatic',
            'REQUIRED_VARIABLES': ['path'],
            'BOOKMARKS': True,
            'HASH': '2650624fea60bc06b75cdcb3b27e81709eab818114a85a6296c8215db5cb60b4',
        },

        'SEASONS': {
           'OPERATION': 'SeriesDetailPageStatic',
           'REQUIRED_VARIABLES': ['path', 'licenseFilter'],
           'BOOKMARKS': True,
           'HASH': 'd113d5b8bf37edd7f4df47107b001068ea544017a37de8450228c59a182ad34b',
        },

        'EPISODES': {
            'OPERATION': 'Season',
            'REQUIRED_VARIABLES': ['id', 'licenseFilter', 'first', 'offset'],
            'BOOKMARKS': True,
            'HASH': '6d132a81ce135faa784712b9a4a136a4d1a0895cd0bb8e83948b0730487b919b',
        },

        'EPG': {
            'QUERY': '($first: Int!) { brands { __typename id livestream { __typename id title quality epg(first: $first) { __typename id startDate endDate '\
                'title secondaryTitle images { __typename id  type url } } } logo { __typename  url } hasVodContent title } }',
            'OPERATION': 'getEpg',
            'REQUIRED_VARIABLES': ['first'],
            'NO_CACHE': True,
        },

        'SEARCH': {
            'OPERATION': 'SearchQ',
            'REQUIRED_VARIABLES': ['text'],
            'NO_CACHE': True,
            'BOOKMARKS': True,
            'HASH': 'f404d5159f3e4973b9bff892fe1a0b06dfbddac2dfe7e45fd14b24fdcba3381e',
        },

        'ACCOUNT': {
            'OPERATION': 'GetAccountInfo',
            'NO_CACHE': True,
            'HASH': '576238419977667cca1bcd3bf481eda75f059d9f9094f8220865e3ce9ac951b9',
        },

        'LANEBOOKMARK': {
            'OPERATION': 'LaneBookmark',
            'REQUIRED_VARIABLES': ['blockId'],
            'BOOKMARKS': True,
            'HASH': '595f5f6a3bb6ec94c98ad0d24b7d5f353fa447376c2628324d25c96bcdd3ec82',
        },

        'MEBOOKMARK': {
            'OPERATION': 'MeBookmark',
            'BOOKMARKS': True,
            'HASH': '5bd7bf0a7ec62faf7d76ad39712e647af69488b0d8e574db1f53c0d89b8b4d53',
        },

        'ADD_BOOKMARK': {
            'QUERY': '($assetId: ID!) {setBookmark(assetId:$assetId) { __typename}}',
            'OPERATION': 'setBookmarkMutation',
            'REQUIRED_VARIABLES': ['assetId'],
            'IS_MUTATION': True,
            'NO_CACHE': True,
        },

        'DEL_BOOKMARK': {
            'QUERY': '($assetId: ID!) { removeBookmark(assetId:$assetId) }',
            'OPERATION': 'removeBookmarkMutation',
            'REQUIRED_VARIABLES': ['assetId'],
            'IS_MUTATION': True,
            'NO_CACHE': True,
        },

        'RESUMELANE': {
            'OPERATION': 'ResumeLaneWithToken',
            'REQUIRED_VARIABLES': ['blockId'],
            'BOOKMARKS': True,
            'HASH': 'a266678285cd887fe488fa9b96693b9467c07a7e779c82ddce92e5656ca29e40',
        },

        'RESUMEPOSITIONS': {
            'OPERATION': 'ResumePositionsWithToken',
            'REQUIRED_VARIABLES': ['ids'],
            'BOOKMARKS': True,
            'HASH': '362a1247c64705097a83a48dc5fb99a29dd573fe276f0b2fb91e50c165752e0b',
        },

        'SET_RESUME_POSITION': {
            'QUERY': '($assetId: ID!, $position: Int!) { setResumePosition(assetId:$assetId, position:$position) { __typename '\
                'assetId position } }',
            'OPERATION': 'setResumeMutation',
            'IS_MUTATION': True,
            'NO_CACHE': True,
        },
    },

    'CATEGORY_LANES': ['StandardLane', 'CollectionLane', 'FeaturedLane', 'LiveLane'],
    'COLLECTION_LANES': ['StandardLane'],
    'COLLECTION_GRID': ['Grid'],
}
