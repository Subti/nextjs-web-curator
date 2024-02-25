import { NextComponentType } from "next";
import { DataProvider } from "@/context/DataContext";
import "../app/globals.css";

export default function MyApp({
  Component,
  pageProps
}: {
  Component: NextComponentType;
  pageProps: any;
}) {
  return (
    <DataProvider>
      <Component {...pageProps} />
    </DataProvider>
  );
}
