import React, { useState, MouseEvent, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

const DisplayImage: React.FC = () => {
  const [rectangles, setRectangles] = useState<Rectangle[]>([]);
  const [currentRect, setCurrentRect] = useState<Rectangle | null>(null);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null);
  const [imageBounds, setImageBounds] = useState<DOMRect | null>(null);
  const [selectedRectangleIndex, setSelectedRectangleIndex] = useState<number | null>(null);

  const imageRef = useRef<HTMLImageElement | null>(null);

  const router = useRouter();
  const protocol = router.query.protocol;
  const num_samples = router.query.num_samples;
  const sample_rate = router.query.sample_rate;
  const filename = router.query.filename;
  const imageUrl = decodeURIComponent(router.query.image_url as string);

  useEffect(() => {
    if (imageRef.current) {
      setImageBounds(imageRef.current.getBoundingClientRect());
    }
  }, [imageRef.current]);

  const handleImageLoad = () => {
    if (imageRef.current) {
      setImageBounds(imageRef.current.getBoundingClientRect());
    }
  };

  const handleMouseDown = (e: MouseEvent) => {
    if (!imageBounds || selectedRectangleIndex !== null) return; // Prevent drawing new boxes when a box is selected
    const x = e.clientX - imageBounds.left;
    const y = e.clientY - imageBounds.top;

    const minImageWidth = imageBounds.width * 0.125; // Constrict bounding box to % of image width (start point)
    const maxImageWidth = imageBounds.width * 0.899; // Constrict bounding box to % of image width (end point)

    const minImageHeight = imageBounds.height * 0.465; // Constrict bounding box to % of image height (start point)
    const maxImageHeight = imageBounds.height * 0.877; // Constrict bounding box to % of image height (end point)

    if (x < minImageWidth || x > maxImageWidth || y < minImageHeight || y > maxImageHeight) return;

    const clickedRectangleIndex = rectangles.findIndex(
      rect =>
        x >= rect.x &&
        x <= rect.x + rect.width &&
        y >= rect.y &&
        y <= rect.y + rect.height
    );
    if (clickedRectangleIndex !== -1) {
      setSelectedRectangleIndex(clickedRectangleIndex);
    } else {
      setStartPoint({ x, y });
      setCurrentRect({ x, y, width: 0, height: 0 });
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!currentRect || !startPoint || !imageBounds) return;
    requestAnimationFrame(() => {
      let width = e.clientX - startPoint.x - imageBounds.left;
      let height = e.clientY - startPoint.y - imageBounds.top;

      const minImageWidth = imageBounds.width * 0.125; // Cosntrict drawing to % of image width (start point)
      const maxImageWidth = imageBounds.width * 0.899; // Constrict drawing to % of image width (end point)

      const minImageHeight = imageBounds.height * 0.465; // Constrict drawing to % of image height (start point)
      const maxImageHeight = imageBounds.height * 0.877; // Constrict drawing to % of image height (end point)

      if (startPoint.x + width < minImageWidth) {
        width = minImageWidth - startPoint.x;
      } else if (startPoint.x + width > maxImageWidth) {
        width = maxImageWidth - startPoint.x;
      }

      if (startPoint.y + height < minImageHeight) {
        height = minImageHeight - startPoint.y;
      } else if (startPoint.y + height > maxImageHeight) {
        height = maxImageHeight - startPoint.y;
      }

      setCurrentRect({
        x: width > 0 ? startPoint.x : startPoint.x + width,
        y: height > 0 ? startPoint.y : startPoint.y + height,
        width: Math.abs(width),
        height: Math.abs(height),
      });
    });
  };

  const handleMouseUp = () => {
    if (!currentRect) return;
    setRectangles([...rectangles, currentRect]);
    setCurrentRect(null);
    setStartPoint(null);
  };

  const handleDelete = (i: number) => {
    setRectangles((rects) => rects.filter((_, index) => index !== i));
    setSelectedRectangleIndex(null);
  };

  const convertToCutPoints = (rectangles: Rectangle[], imageWidth: number, numSamples: number) => {
    const maxTime = (numSamples / 10000000) * 500; // Calculate the maximum time based on the num_samples

    const minImageWidth = imageWidth * 0.125; // Start of the constricted part
    const maxImageWidth = imageWidth * 0.899; // End of the constricted part
    const constrictedWidth = maxImageWidth - minImageWidth; // Width of the constricted part

    return rectangles.map(rect => {
      const start = Math.round(((rect.x - minImageWidth) / constrictedWidth) * maxTime);
      const end = Math.round((((rect.x + rect.width) - minImageWidth) / constrictedWidth) * maxTime);
      return `${start} ${end}`;
    });
  };

  const handleSubmit = async () => {
    if (!imageBounds) return;
    const cutPoints = convertToCutPoints(rectangles, imageBounds.width, Number(num_samples)).join(' ');

    const formData = new FormData();
    formData.append('action', 'save');
    formData.append('cuts', cutPoints);
    if (typeof protocol === 'string') {
      formData.append('protocol', protocol);
    }
    if (typeof filename === 'string') {
      formData.append('filename', filename);
    }
    if (typeof num_samples === 'string') {
      formData.append('num_samples', num_samples);
    }
    if (typeof sample_rate === 'string') {
      formData.append('sample_rate', sample_rate);
    }

    const response = await fetch('http://localhost:8000/result', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    console.log(data);
  };

  return (
    <div
      style={{ position: 'relative' }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
    >
      <img
        ref={imageRef}
        src={imageUrl}
        alt="Generated"
        style={{ position: 'absolute', transform: 'scale(1)', transformOrigin: 'top left' }} // Test scaling here by changing the scale number to whatever you want
        onLoad={handleImageLoad}
      />
      {rectangles.map((rect, i) => (
        <div
          key={i}
          style={{
            border: '1px solid red',
            position: 'absolute',
            left: `${rect.x}px`,
            top: `${rect.y}px`,
            width: `${rect.width}px`,
            height: `${rect.height}px`,
          }}
        >
          {i === selectedRectangleIndex && (
            <>
              <button style={{ position: 'absolute', right: 0, top: 0 }} onClick={() => handleDelete(i)}>
                Delete
              </button>
              <button style={{ position: 'absolute', right: 0, bottom: 0 }} onClick={() => setSelectedRectangleIndex(null)}>
                Deselect
              </button>
            </>
          )}
        </div>
      ))}
      {currentRect && (
        <div
          style={{
            border: '1px solid red',
            position: 'absolute',
            left: `${currentRect.x}px`,
            top: `${currentRect.y}px`,
            width: `${currentRect.width}px`,
            height: `${currentRect.height}px`,
          }}
        />
      )}
      <button style={{ position: 'absolute', top: 0, right: 0, padding: '10px', backgroundColor: 'blue', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }} onClick={handleSubmit}>
        Submit
      </button>
    </div>
  );
};

export default DisplayImage;