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

    const minImageWidth = imageBounds.width * 0.125; // 12.5% of the image width
    const maxImageWidth = imageBounds.width * 0.899; // 87.5% of the image width

    const minImageHeight = imageBounds.height * 0.465; // 12.5% of the image height
    const maxImageHeight = imageBounds.height * 0.877; // 87.5% of the image height

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

      const minImageWidth = imageBounds.width * 0.125; // 12.5% of the image width
      const maxImageWidth = imageBounds.width * 0.899; // 87.5% of the image width

      const minImageHeight = imageBounds.height * 0.465; // 12.5% of the image height
      const maxImageHeight = imageBounds.height * 0.877; // 87.5% of the image height

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
    </div>
  );
};

export default DisplayImage;