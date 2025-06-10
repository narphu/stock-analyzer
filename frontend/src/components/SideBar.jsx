import { HomeIcon, ChartBarIcon } from '@heroicons/react/24/outline';

export default function SideBar() {
  return (
    <div className="w-64 h-screen bg-gray-900 text-white p-4">
      <h1 className="text-2xl font-bold mb-6">📊 Stock Analyzer</h1>
      <nav className="space-y-4">
        <a href="#" className="flex items-center gap-2 text-gray-300 hover:text-white">
          <HomeIcon className="h-5 w-5" />
          Dashboard
        </a>
        <a href="#" className="flex items-center gap-2 text-gray-300 hover:text-white">
          <ChartBarIcon className="h-5 w-5" />
          Trends
        </a>
      </nav>
    </div>
  );
}
