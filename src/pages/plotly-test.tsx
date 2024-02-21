import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';

// Dynamically import Plot component
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

const DisplayPlot: React.FC = () => {
  const router = useRouter();
  const dataUrl = router.query.data_url ? decodeURIComponent(router.query.data_url as string) : null;

  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (dataUrl) {
      console.log(`Fetching data from ${dataUrl}...`);
      fetch(dataUrl)
        .then(response => {
          console.log('Server response:', response);
          return response.json();
        })
        .then(data => {
          console.log('Data:', data);
          setData(data);
        });
    }
  }, [dataUrl]);

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {(Plot as any)({
        data: [
          {
            x: data.time_series.t,
            y: data.time_series.i,
            type: 'scatter',
            mode: 'lines',
            name: 'I',
            line: { color: 'blue' },
          },
          {
            x: data.time_series.t,
            y: data.time_series.q,
            type: 'scatter',
            mode: 'lines',
            name: 'Q',
            line: { color: 'red' },
          },
          {
            x: data.spectrogram.t,
            y: data.spectrogram.f,
            z: data.spectrogram.Sxx,
            type: 'heatmap',
            showscale: false,
          },
        ],
        layout: { autosize: true, title: 'Spectrogram' },
      })}
    </div>
  );
};

export default DisplayPlot;