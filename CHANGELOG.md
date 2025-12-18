# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2025-12-03

- Update for Python 3.13 (#150)
- Add new severity level 'VERY LOW' (#148)
- Add protection against missing 'notify' param (#142)
- Add status field to update_ticket (#139)
- Add .tar releases (#131)

## [2.2.0] - 2024-12-09

- Released only for UIC
- Update to use NiceBaseConnector (#116)
- Add phantom-toolbox to requirements files and `Makefile` (#114)
- Move hard coded translation tables to app.json config (#126)
- Add 'Get Current Release' and 'Upload Release Asset' steps to deploy.yml (#118)

## [2.1.0] - 2024-07-31

- Add `update` action block
- Add ability to set `Description`, `Incident Severity`, `Form`, `Assignee`, `Responsible Group`
- Fix for unset `Status` field
- Update `create` action to return `ticket_id`

### [2.0.0] - 2023-09-21

### Breaking Changes

This release requires deleting the previous deployed TDX SOAR App.
This release requires deleting and re-creating the SOAR `configured asset`.

- Update package metadata
- Update config keys (#48)
  - Organization Name is no longer required (#40)
  - Pin TDXLIB (#44)

### Added

- Add `reassign` block (#38)
- Add `update_ticket` block (#27)
- Add error handling (#28)
- Add simpler test_connectivity (#4)

## [1.0.0] - 2022-05-17

### Added

- Initial release
- Prototype SOAR TDX app (#1)
- Provides `test_connectivity` and `create_ticket`
