import PredictionGauge from './PredictionGauge';

export default function Dashboard({ predictions }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-6 p-6">
      {predictions.map((item) => (
        <PredictionGauge
          key={item.days}
          label={item.days + ' day' + (item.days > 1 ? 's' : '')}
          value={item.price}
          date={item.date}
        />
      ))}
    </div>
  );
}
