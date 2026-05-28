export const Toggle = ({ checked, onChange, label }) => {
  return (
    <div className="flex items-center gap-3">
      <button
        onClick={() => onChange(!checked)}
        className={`w-12 h-6 rounded-full transition-colors ${
          checked ? 'bg-primary-600' : 'bg-dark-600'
        }`}
      >
        <div
          className={`w-5 h-5 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-0.5'
          }`}
        />
      </button>
      {label && <span className="text-white">{label}</span>}
    </div>
  );
};
