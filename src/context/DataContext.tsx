import React, { createContext, useContext, useState, ReactNode } from "react";

// Define the type for children
interface Props {
  children: ReactNode;
}

interface ContextType {
  fetchedData1: null | any; // Change 'any' to the type of your data if known
  setFetchedData1: React.Dispatch<React.SetStateAction<null | any>>;
  fetchedData2: null | any; // Change 'any' to the type of your data if known
  setFetchedData2: React.Dispatch<React.SetStateAction<null | any>>;
}

const DataContext = createContext<ContextType | null>(null);

export const DataProvider = ({ children }: Props) => {
  const [fetchedData1, setFetchedData1] = useState(null);
  const [fetchedData2, setFetchedData2] = useState(null);

  return (
    <DataContext.Provider
      value={{ fetchedData1, setFetchedData1, fetchedData2, setFetchedData2 }}
    >
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => useContext(DataContext);
