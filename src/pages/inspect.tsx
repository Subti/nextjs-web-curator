import React, { useState, MouseEvent, useRef, useEffect } from "react";
import { useRouter } from "next/router";
import ReviewSettings from "@/app/components/ReviewSettings";
import Button from "@/app/components/Button";

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface InspectProps {
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setLoadingText: React.Dispatch<React.SetStateAction<string>>;
  setCapture: React.Dispatch<React.SetStateAction<boolean>>;
  setInspect: React.Dispatch<React.SetStateAction<boolean>>;
  setSliced: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function Inspect({
  setCapture,
  setInspect,
  setLoading,
  setLoadingText,
  setSliced
}: InspectProps) {
  // const router = useRouter();

  // States from the original Inspect component
  const [protocol, setProtocol] = useState("");
  const [numSamples, setNumSamples] = useState(0);
  const [sampleRate, setSampleRate] = useState(0);
  const [filename, setFilename] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [metaData, setMetaData] = useState({});
  const [captureSettings, setCaptureSettings] = useState({});
  const [recordingSummary, setRecordingSummary] = useState({});

  // States from the DisplayImage component
  const [rectangles, setRectangles] = useState<Rectangle[]>([]);
  const [currentRect, setCurrentRect] = useState<Rectangle | null>(null);
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(
    null
  );
  const [currentDivBounds, setCurrentDivBounds] = useState<DOMRect | null>(
    null
  );
  const [selectedRectangleIndex, setSelectedRectangleIndex] = useState<
    number | null
  >(null);
  const [cutPoints, setCutPoints] = useState<string[]>([]);

  const imageRef = useRef<HTMLImageElement | null>(null);

  // Fetch data on component mount
  useEffect(() => {
    fetch("http://localhost:8000/formvalues")
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setProtocol(data.protocol);
        setNumSamples(data.num_samples);
        setSampleRate(data.sample_rate);
        setFilename(data.filename);
        setImageUrl(data.image_url._url);
        setMetaData(data.metadata.metadata);
        setCaptureSettings(data.capture_args);
        setRecordingSummary(data.rec_args);
      })
      .catch((error) => console.error("Error:", error));
  }, []);

  useEffect(() => {
    if (imageRef.current) {
      const mainDiv = document.getElementById("mainDiv");
      setCurrentDivBounds(mainDiv?.getBoundingClientRect() ?? null);
    }
  }, [imageRef.current]);

  const handleImageLoad = () => {
    if (imageRef.current) {
      const mainDiv = document.getElementById("mainDiv");
      setCurrentDivBounds(mainDiv?.getBoundingClientRect() ?? null);
    }
  };

  const handleMouseDown = (e: MouseEvent) => {
    if (selectedRectangleIndex !== null) return; // Prevent drawing new boxes when a box is selected
    const mainDiv = document.getElementById("mainDiv");
    if (!mainDiv) return;
    const mainDivBounds = mainDiv.getBoundingClientRect();

    // Use mainDivBounds instead of imageBounds to calculate the positions
    const x = e.clientX - mainDivBounds.left;
    const y = e.clientY - mainDivBounds.top;

    const minImageWidth = mainDivBounds.width * 0.125; // Constrict bounding box to % of image width (start point)
    const maxImageWidth = mainDivBounds.width * 0.899; // Constrict bounding box to % of image width (end point)

    const minImageHeight = mainDivBounds.height * 0.465; // Constrict bounding box to % of image height (start point)
    const maxImageHeight = mainDivBounds.height * 0.877; // Constrict bounding box to % of image height (end point)

    if (
      x < minImageWidth ||
      x > maxImageWidth ||
      y < minImageHeight ||
      y > maxImageHeight
    )
      return;

    const clickedRectangleIndex = rectangles.findIndex(
      (rect) =>
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
    if (!currentRect || !startPoint) return;
    const mainDiv = document.getElementById("mainDiv");
    if (!mainDiv || !currentRect || !startPoint) return;
    const mainDivBounds = mainDiv.getBoundingClientRect();

    // Use mainDivBounds instead of imageBounds to calculate the positions
    requestAnimationFrame(() => {
      let width = e.clientX - startPoint.x - mainDivBounds.left;
      let height = e.clientY - startPoint.y - mainDivBounds.top;

      const minImageWidth = mainDivBounds.width * 0.125; // Cosntrict drawing to % of image width (start point)
      const maxImageWidth = mainDivBounds.width * 0.899; // Constrict drawing to % of image width (end point)

      const minImageHeight = mainDivBounds.height * 0.465; // Constrict drawing to % of image height (start point)
      const maxImageHeight = mainDivBounds.height * 0.877; // Constrict drawing to % of image height (end point)

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
        height: Math.abs(height)
      });
    });
  };

  const handleMouseUp = () => {
    if (!currentRect || !currentDivBounds) return;

    // Check if the new rectangle would overlap with any existing rectangles
    const wouldOverlap = rectangles.some(
      (rect) =>
        currentRect.x < rect.x + rect.width &&
        currentRect.x + currentRect.width > rect.x &&
        currentRect.y < rect.y + rect.height &&
        currentRect.y + currentRect.height > rect.y
    );
    if (wouldOverlap) {
      // If the new rectangle would overlap, show an alert and don't add it
      alert("You cannot overlap the bounding boxes.");
      setCurrentRect(null);
      setStartPoint(null);
      return;
    }

    const newRectangles = [
      ...rectangles,
      { ...currentRect, id: Date.now().toString() }
    ];
    setRectangles(newRectangles);
    setCurrentRect(null);
    setStartPoint(null);

    // Calculate cutPoints immediately after a rectangle is drawn
    const newCutPoints = convertToCutPoints(
      newRectangles,
      currentDivBounds.width,
      Number(numSamples)
    );
    setCutPoints(newCutPoints);
    console.log(newCutPoints);
  };

  const handleDelete = (i: number) => {
    setRectangles((rects) => rects.filter((_, index) => index !== i));
    setSelectedRectangleIndex(null);
  };

  const convertToCutPoints = (
    rectangles: Rectangle[],
    imageWidth: number,
    numSamples: number
  ) => {
    const maxTime = (numSamples / 10000000) * 500; // Calculate the maximum time based on the num_samples

    const minImageWidth = imageWidth * 0.125; // Start of the constricted part
    const maxImageWidth = imageWidth * 0.899; // End of the constricted part
    const constrictedWidth = maxImageWidth - minImageWidth; // Width of the constricted part

    return rectangles.map((rect) => {
      const start = Math.round(
        ((rect.x - minImageWidth) / constrictedWidth) * maxTime
      );
      const end = Math.round(
        ((rect.x + rect.width - minImageWidth) / constrictedWidth) * maxTime
      );
      return `${start} ${end}`;
    });
  };

  const calculateCutPointPosition = (
    rectangle: Rectangle,
    cutPoint: string,
    imageWidth: number
  ) => {
    const [start, end] = cutPoint.split(" ").map(Number);
    const maxTime = (Number(numSamples) / 10000000) * 500; // Calculate the maximum time based on the num_samples

    const minImageWidth = imageWidth * 0.125; // Start of the constricted part
    const maxImageWidth = imageWidth * 0.899; // End of the constricted part
    const constrictedWidth = maxImageWidth - minImageWidth; // Width of the constricted part

    const startPosition = (start / maxTime) * constrictedWidth + minImageWidth;
    const endPosition = (end / maxTime) * constrictedWidth + minImageWidth;

    return { start: startPosition, end: endPosition };
  };

  const handleSubmit = async () => {
    if (!currentDivBounds) return;

    const cutPoints = convertToCutPoints(
      rectangles,
      currentDivBounds.width,
      Number(numSamples)
    ).join(" ");

    const formData = new FormData();
    formData.append("action", "save");
    formData.append("cuts", cutPoints);
    console.log(cutPoints);
    console.log(protocol);
    console.log(filename);
    console.log(numSamples);
    console.log(sampleRate);
    if (typeof protocol === "string") {
      formData.append("protocol", protocol);
    }
    if (typeof filename === "string") {
      formData.append("filename", filename);
    }
    formData.append("num_samples", numSamples.toString());
    formData.append("sample_rate", sampleRate.toString());

    try {
      setLoadingText("Slicing Capture");
      setLoading(true);
      toggleWindow();
      const response = await fetch("http://localhost:8000/result", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // Optionally, process response data here
      const data = await response.json();
      console.log(data);
      if (data) {
        setTimeout(() => {
          setInspect(false);
          setLoading(false);
          setSliced(true);
        }, 2000);
      }

      // router.push("/sliced-images");

      // Redirect to the sliced-images page only after the fetch request is successfully completed
    } catch (error) {
      console.error(
        "There has been a problem with your fetch operation:",
        error
      );
    }
  };

  const toggleWindow = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const discardAndCaptureNew = async () => {
    // router.push("/");
    setLoadingText("Discarding Capture");
    setLoading(true);
    toggleWindow();

    const formData = new FormData();
    formData.append("action", "discard");
    formData.append("filename", `${filename}`);

    try {
      const response = await fetch("http://localhost:8000/result", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        console.error("HTTP error", response.status);
      } else {
        const data = await response.text();
        if (data) {
          setTimeout(() => {
            setInspect(false);
            setLoading(false);
            setCapture(true);
          }, 2000);
        }
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <>
      <div className="flex justify-between w-[90%] mb-5">
        <ReviewSettings title="Recording Summary" formData={recordingSummary} />
        <ReviewSettings
          title="SDR Capture Settings"
          formData={captureSettings}
        />
        <ReviewSettings title="Metadata" formData={metaData} />
      </div>

      <div
        id="mainDiv"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        style={{ position: "relative" }} // Ensure relative positioning for child absolute elements
      >
        <img
          ref={imageRef}
          src={imageUrl}
          alt="Generated"
          onLoad={handleImageLoad}
          style={{ transformOrigin: "top left" }} // Adjust as necessary
        />
        {/* Rectangles rendering */}
        {currentDivBounds &&
          rectangles.map((rect, i) => {
            const cutPoint = cutPoints[i];
            let start = 0;
            let end = 0;
            if (cutPoint) {
              const positions = calculateCutPointPosition(
                rect,
                cutPoint,
                currentDivBounds.width
              );
              start = positions.start;
              end = positions.end;
            }
            return (
              <React.Fragment key={i}>
                <div
                  style={{
                    borderLeft: "2px dashed black",
                    position: "absolute",
                    left: `${rect.x}px`,
                    top: `${currentDivBounds.height / 20}px`,
                    height: `${currentDivBounds.height / 2.45}px`
                  }}
                />
                {cutPoint && (
                  <div
                    style={{
                      position: "absolute",
                      left: `${start}px`,
                      top: `${currentDivBounds.height / 20}px`,
                      width: `${end - start}px`,
                      height: `${currentDivBounds.height / 2.45}px`,
                      backgroundColor: "rgba(255, 0, 0, 0.5)"
                    }}
                  >
                    {`Start: ${cutPoint.split(" ")[0]}, End: ${
                      cutPoint.split(" ")[1]
                    }`}
                  </div>
                )}
                <div
                  style={{
                    borderLeft: "2px dashed black",
                    position: "absolute",
                    left: `${rect.x + rect.width}px`,
                    top: `${currentDivBounds.height / 20}px`,
                    height: `${currentDivBounds.height / 2.45}px`
                  }}
                />
                <div
                  style={{
                    border: "1px solid red",
                    position: "absolute",
                    left: `${rect.x}px`,
                    top: `${rect.y}px`,
                    width: `${rect.width}px`,
                    height: `${rect.height}px`
                  }}
                >
                  {i === selectedRectangleIndex && (
                    <>
                      <button
                        style={{ position: "absolute", right: 0, top: 0 }}
                        onClick={() => handleDelete(i)}
                      >
                        Delete
                      </button>
                      <button
                        style={{ position: "absolute", right: 0, bottom: 0 }}
                        onClick={() => setSelectedRectangleIndex(null)}
                      >
                        Deselect
                      </button>
                    </>
                  )}
                </div>
              </React.Fragment>
            );
          })}
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
      <div className="flex justify-center w-full my-10 gap-5">
        <Button
          text="Discard and Capture New"
          type="button"
          textSize="xl"
          onClick={discardAndCaptureNew}
        />
        <Button
          text="Slice"
          type="button"
          textSize="xl"
          onClick={handleSubmit}
        />
      </div>
    </>
  );
}
