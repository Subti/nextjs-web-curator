import Button from "./components/Button";
import Column from "./components/Column";
import Header from "./components/Header";
import Row from "./components/Row";

export default function Home() {
  return (
    <>
      <main className="flex flex-col items-center justify-center">
        <Header />
        <Row />
        <Button />
      </main>
    </>
  );
}
