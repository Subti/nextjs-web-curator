import React, { useState, MouseEvent, useRef, useEffect } from "react";
import { useRouter } from "next/router";
import Header from "@/app/components/Header"; // Importing Header component
import ReviewSettings from "@/app/components/ReviewSettings";
import Button from "@/app/components/Button";

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

export default function Inspect(props: any) {
  const [rectangles, setRectangles] = useState<Rectangle[]>([]);
  const [currentRect, setCurrentRect] = useState<Rectangle | null>(null);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(
    null
  );
  const [imageBounds, setImageBounds] = useState<DOMRect | null>(null);

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
    if (!imageBounds) return;
    const x = e.clientX - imageBounds.left;
    const y = e.clientY - imageBounds.top;
    if (x < 0 || x > imageBounds.width || y < 0 || y > imageBounds.height)
      return;
    setStartPoint({ x, y });
    setCurrentRect({ x, y, width: 0, height: 0 });
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!currentRect || !startPoint || !imageBounds) return;
    let width = e.clientX - startPoint.x - imageBounds.left;
    let height = e.clientY - startPoint.y - imageBounds.top;
    if (width < 0) {
      width = Math.max(width, -startPoint.x);
    } else if (startPoint.x + width > imageBounds.width) {
      width = imageBounds.width - startPoint.x;
    }
    if (height < 0) {
      height = Math.max(height, -startPoint.y);
    } else if (startPoint.y + height > imageBounds.height) {
      height = imageBounds.height - startPoint.y;
    }
    setCurrentRect({
      x: width > 0 ? startPoint.x : startPoint.x + width,
      y: height > 0 ? startPoint.y : startPoint.y + height,
      width: Math.abs(width),
      height: Math.abs(height)
    });
  };

  const handleMouseUp = () => {
    if (!currentRect) return;
    setRectangles([...rectangles, currentRect]);
    setCurrentRect(null);
    setStartPoint(null);
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <Header title="Inspect Recording" />
      <div className="flex justify-around w-3/4">
        <ReviewSettings />
        <ReviewSettings />
        <ReviewSettings />
      </div>
      <div
        style={{ position: "relative" }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <img
          ref={imageRef}
          src={imageUrl}
          alt="Generated"
          style={{ position: "relative" }}
          onLoad={handleImageLoad}
        />
        {rectangles.map((rect, i) => (
          <div
            key={i}
            style={{
              border: "1px solid red",
              position: "absolute",
              left: `${rect.x}px`,
              top: `${rect.y}px`,
              width: `${rect.width}px`,
              height: `${rect.height}px`
            }}
          />
        ))}
        {currentRect && (
          <div
            style={{
              border: "1px solid red",
              position: "absolute",
              left: `${currentRect.x}px`,
              top: `${currentRect.y}px`,
              width: `${currentRect.width}px`,
              height: `${currentRect.height}px`
            }}
          />
        )}
      </div>
      <Button text="Discard and Capture New" />
    </div>
  );
}

// min-h-screen
