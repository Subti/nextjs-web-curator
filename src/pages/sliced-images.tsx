import { useEffect, useState } from 'react';

interface Data {
  files: string[];
  image_urls: string[];
}

const SlicedImages = () => {
  const [data, setData] = useState<Data | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/result')
      .then(response => response.json())
      .then((data: Data) => {
        setData(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {data && data.image_urls.map((url, index) => (
        <img key={index} src={url} alt={`Sliced Image ${index}`} />
      ))}
    </div>
  );
};

export default SlicedImages;