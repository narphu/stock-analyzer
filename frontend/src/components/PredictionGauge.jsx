import { RadialBarChart, RadialBar, Legend } from 'recharts';

export default function PredictionGauge({ label, value, date }) {
  const data = [{ name: label, value }];

  return (
    <div className="bg-white rounded-lg shadow p-4 text-center">
      <h2 className="font-semibold mb-1">{label}</h2>
      <p className="text-sm text-gray-500 mb-2">{date}</p>
      <RadialBarChart width={200} height={150} innerRadius="70%" outerRadius="100%" data={data}>
        <RadialBar minAngle={15} clockWise dataKey="value" />
        <Legend />
      </RadialBarChart>
      <p className="text-xl font-bold mt-2">${value.toFixed(2)}</p>
    </div>
  );
}
