import { NextComponentType } from "next";
import "../app/globals.css";

export default function MyApp({
  Component,
  pageProps
}: {
  Component: NextComponentType;
  pageProps: any;
}) {
  return <Component {...pageProps} />;
}
