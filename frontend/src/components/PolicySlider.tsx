export function PolicySlider({
  label,
  value,
  min,
  max,
  step = 1,
  suffix = "",
  onChange,
  helper,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
  onChange: (value: number) => void;
  helper?: string;
}) {
  return (
    <div className="slider-row">
      <div className="slider-head">
        <strong>{label}</strong>
        <span>{value}{suffix}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} />
      {helper ? <div className="field-block helper">{helper}</div> : null}
    </div>
  );
}
