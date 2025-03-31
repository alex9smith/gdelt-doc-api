# Changelog

## Unreleased

Handle empty API responses in timeline search

## 1.10.2

Fix `Unpack` type hint for older Python versions (#60)

## 1.10.1

Add workaround for domain bug to filter docstring (#54)
Handle 0 results in timeline search (#55)

## 1.10.0

Add support for `tone` and `tone_absolute` filters (#51)
Fix type hints in filters (#50)

## 1.9.0

Fix JSONDecodeError when loading bad responses from the API (#47)

## 1.8.0

Add multiple nears (#31)(#45)

## 1.7.0

Add the ability to filter based on 3 letter language (#38)

## 1.6.0

Only support Python 3.10 and above (#39)
Format all files with prettier (#40)
Update package dependencies (#41)

## 1.5.0

Provide user agent in requests to the API (#22)

## 1.4.0

Validate `timespan` filter parameter to make sure it's an allowed value
Catch API errors when a query string is invalid and return them to the user

## 1.3.3

Fix a bug in `multi_repeat` which meant any filter using `OR` would fail

## 1.3.2

Fix a bug in `multi_repeat` which caused a bad response from the API which could not be parsed

## 1.3.1

Fix bug when only the first of the filter conditions (eg. keyword, near, etc.) was used

## 1.3.0

Recursively load the JSON response to remove improper characters

## 1.2.0

Add support for filtering by timespan instead of start and end date

## 1.1.0

Adds support for multiple repeat filters

## 1.0.0

First version released
