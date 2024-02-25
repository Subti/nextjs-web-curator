import React, { createContext, useContext, useState, ReactNode } from "react";

// Define the type for children
interface Props {
  children: ReactNode;
}

interface CaptureSettingsData {
  image_url: { _url: string };
  rec_args: {
    /* rec_args properties */
  };
  capture_args: {
    /* capture_args properties */
  };
  metadata: {
    /* metadata properties */
  };
}

interface ContextType {
  captureSettingsData: CaptureSettingsData | any; // Change 'any' to the type of your data if known
  setCaptureSettingsData: React.Dispatch<
    React.SetStateAction<CaptureSettingsData | any>
  >;
}

const DataContext = createContext<ContextType | null>(null);

export const DataProvider = ({ children }: Props) => {
  const [captureSettingsData, setCaptureSettingsData] = useState<
    CaptureSettingsData | any
  >(null);

  const contextValue: ContextType = {
    captureSettingsData,
    setCaptureSettingsData
  };

  return (
    <DataContext.Provider value={contextValue}>{children}</DataContext.Provider>
  );
};

// Custom hook to access context
export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useData must be used within a DataProvider");
  }
  return context;
};
