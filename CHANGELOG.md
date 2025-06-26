# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.3] - 2025-06-20

### Fixed
- ✅ **Home Assistant 2025 Compatibility**: Fixed "sensor no longer has a state class" error by adding proper `state_class` definitions to all sensors
- ✅ **GitHub Validation Issues**: 
  - Fixed HACS validation by removing invalid `domains` and `iot_class` keys from hacs.json
  - Fixed flake8 validation with proper Python code formatting, line length compliance, and removal of unused imports
- ✅ **Sensor State Classes**: Added proper `state_class="measurement"` to progress and processing time sensors
- ✅ **Code Quality**: All Python files now meet PEP8 standards with proper formatting

### Added
- ✅ **Options Flow**: Users can now reconfigure integration settings after initial setup
  - Change update intervals (1-24 hours)
  - Modify prediction times
  - Enable/disable weekend analysis
  - Adjust confidence thresholds (10-95%)
  - Set maximum prediction change limits (1-10%)
- ✅ **Reconfiguration Support**: API keys and basic settings can be changed via the "Configure" button
- ✅ **Enhanced Error Handling**: Better API validation and user-friendly error messages
- ✅ **Configuration Options**: More granular control over analysis parameters

### Improved
- ✅ **Integration Structure**: Better organization of code with proper flake8 compliance
- ✅ **API Validation**: Real-time validation of API keys during setup and reconfiguration
- ✅ **Documentation**: Updated README with comprehensive setup and troubleshooting guides
- ✅ **GitHub Actions**: Fixed validation workflows to properly test integration quality

## [2.2.2] - 2025-06-18

### Added
- Enhanced multi-source sentiment analysis with 10 financial news sources
- Real-time progress tracking showing current source being analyzed
- Processing time estimates and ETA calculations
- Current source sensor showing which news outlet is being processed

### Improved
- Sentiment analysis now takes 5-10 minutes with visible progress updates
- Weighted source reliability (Bloomberg, Reuters weighted higher)
- Better error recovery and API rate limiting

## [2.2.1] - 2025-06-16

### Fixed
- Home Assistant 2025 syntax compatibility updates
- Automation trigger syntax updated from `platform:` to `trigger:`
- Service calls updated from `service:` to `action:`

### Added
- Python script compatibility with pyscript integration
- Enhanced logging and error reporting

## [2.2.0] - 2025-06-14

### Added
- Multi-source sentiment analysis implementation
- Renaissance Technologies-inspired quantitative algorithm
- Technical analysis with RSI, momentum, moving averages
- Comprehensive prediction confidence scoring

### Features
- S&P 500 and FTSE 100 market direction predictions
- 6 sensor entities with detailed attributes
- Dashboard integration with pre-built cards
- Automation support for market alerts

## [2.1.0] - 2025-06-12

### Added
- Initial integration framework
- Alpha Vantage API integration
- Basic technical analysis implementation
- Home Assistant config flow support

## [2.0.0] - 2025-06-10

### Added
- Complete rewrite as Home Assistant custom integration
- HACS compatibility
- UI-based configuration
- Renaissance Technologies approach implementation