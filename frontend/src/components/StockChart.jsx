import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';

export default function StockChart({ data }) {
  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">Stock Trend</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
