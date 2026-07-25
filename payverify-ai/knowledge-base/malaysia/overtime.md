# Overtime — Malaysia

## Purpose
Compute overtime (OT) pay for hours worked beyond normal hours, differentiated by day type.

## Business Rules (verbatim from source)
- **Normal Working Day**: 1.5× the hourly rate for any work exceeding the regular daily
  limit (over 8 hours).
- **Rest Day**: 2.0× the hourly rate if working beyond normal hours, or specific half/full-day
  ordinary rates if working standard hours on a rest day.
- **Public Holiday**: 3.0× the hourly rate.
- **Hourly Rate of Pay (HRP)**: Monthly Basic Wages ÷ 26 ÷ daily normal working hours
  (usually 8).

## Validation Rules
- `day_type` ∈ {normal_working_day, rest_day, public_holiday}.
- Rest day + standard hours worked (no excess hours) → the source does not give an exact
  multiplier ("specific half/full-day ordinary rates") → `PENDING_SME_VALIDATION`.

## Formula
```
HRP = Monthly Basic Wages / 26 / Daily Normal Hours
OT Pay = HRP x Multiplier x OT Hours
Multiplier: Normal Working Day = 1.5, Rest Day (exceeding normal hours) = 2.0, Public Holiday = 3.0
```

## Examples
- Monthly basic RM2,080, 2h OT on a normal working day: HRP = 2080/26/8 = RM10.00; OT pay =
  10.00 × 1.5 × 2 = RM30.00.

## Exceptions
- Rest-day standard-hours (non-OT) scenario — multiplier not specified in source. Requires
  SME Validation.

## Dependencies
- Monthly Basic Wages, daily normal working hours (default 8), OT hours, day type.

## Metadata
- **Rule ID**: MY_OT_001
- **Source Reference**: `MY Labour law and statutory calculation.txt`
- **Version**: 1.0
- **Effective Date**: Requires SME Validation
- **Status**: Implemented for normal/rest(exceeding)/public-holiday cases; rest-day
  standard-hours sub-case pending SME validation.
