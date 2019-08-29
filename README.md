# GTA Online Friends Cleaner

This tool is designed to remove friends who have been inactive in GTA Online for a certain number of days.

Friends with a hidden profile will be removed unless they are whitelisted. The same applies to friends whose last login date is unknown.

## Whitelisting

A white list with friends and crews names can be created in the user's personal folder (Windows): `%userprofile%\.gtao_friends_cleaner\`.
It must be a text file named `ignore_list.txt` containing one name per line.

The `[friends]` and `[crews]` headers are required before names to differentiate between the friends and crews lists. If no headers are given, the contents of the file are treated as a list of just friends.

### Example of ignore_list.txt

```
[friends]
Friend 1
Friend 2
Friend 3

[crews]
Crew 1
Crew 2
Crew 3
```