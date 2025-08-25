## 1.30.5 - 2025-08-24
### Extractors
#### Additions
- [shimmie2] support `noz.rip/booru` ([#8101](https://github.com/mikf/gallery-dl/issues/8101))
- [sizebooru] add support ([#7667](https://github.com/mikf/gallery-dl/issues/7667))
- [twitter] add `highlights` extractor ([#7826](https://github.com/mikf/gallery-dl/issues/7826))
- [twitter] add `home` extractor ([#7974](https://github.com/mikf/gallery-dl/issues/7974))
#### Fixes
- [aryion] fix pagination ([#8091](https://github.com/mikf/gallery-dl/issues/8091))
- [rule34] support using `api-key` & `user-id` ([#8077](https://github.com/mikf/gallery-dl/issues/8077) [#8088](https://github.com/mikf/gallery-dl/issues/8088) [#8098](https://github.com/mikf/gallery-dl/issues/8098))
- [tumblr:search] fix `ValueError: not enough values to unpack` ([#8079](https://github.com/mikf/gallery-dl/issues/8079))
- [twitter] handle `KeyError: 'result'` for retweets ([#8072](https://github.com/mikf/gallery-dl/issues/8072))
- [zerochan] expect `500 Internal Server Error` responses for HTML requests ([#8097](https://github.com/mikf/gallery-dl/issues/8097))
#### Improvements
- [civitai:search] add `token` option ([#8093](https://github.com/mikf/gallery-dl/issues/8093))
- [instagram] warn about lower quality video downloads ([#7921](https://github.com/mikf/gallery-dl/issues/7921) [#8078](https://github.com/mikf/gallery-dl/issues/8078))
- [instagram] remove `candidates` warning ([#7921](https://github.com/mikf/gallery-dl/issues/7921) [#7989](https://github.com/mikf/gallery-dl/issues/7989) [#8071](https://github.com/mikf/gallery-dl/issues/8071))
- [oauth] improve error messages ([#8086](https://github.com/mikf/gallery-dl/issues/8086))
- [pixiv] distinguish empty from deleted profiles ([#8066](https://github.com/mikf/gallery-dl/issues/8066))
- [twitter] update API endpoint query hashes & parameters
#### Metadata
- [batoto] extract more metadata ([#7994](https://github.com/mikf/gallery-dl/issues/7994))
- [instagram:highlights] extract `author` & `owner` & `user` metadata ([#7846](https://github.com/mikf/gallery-dl/issues/7846))
- [newgrounds] extract `slug` metadata ([#8064](https://github.com/mikf/gallery-dl/issues/8064))
- [twitter] extract `community` metadata ([#7424](https://github.com/mikf/gallery-dl/issues/7424))
#### Removals
- [shimmie2] remove `sizechangebooru.com` ([#7667](https://github.com/mikf/gallery-dl/issues/7667))
- [zzup] remove module ([#4604](https://github.com/mikf/gallery-dl/issues/4604))
### Downloaders
- [ytdl] improve playlist handling ([#8085](https://github.com/mikf/gallery-dl/issues/8085))
### Scripts
- implement `rm` helper script
- add `-g/--git` command-line options
- [util] add `git()` & `lines()` helper functions
### Miscellaneous
- [config] add `conf` argument to `config.load()` ([#8084](https://github.com/mikf/gallery-dl/issues/8084))
