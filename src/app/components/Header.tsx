import React from "react";
import Button from "./Button";
import NavLinks from "../modules/constants";

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  const displayMessage = () => {
    console.log(
      "Take me home, country roads... to the place, I beloooooooong..."
    );
  };

  return (
    <div className="text-4xl text-white flex relative w-full h-[100px] bg-transparent border-b-2 border-white justify-between items-center pl-[8rem] pr-[8rem] mb-4">
      <a
        href="https://www.qoherent.ai"
        target="_blank"
        onMouseEnter={displayMessage}
        onMouseLeave={() => {}}
      >
        <img src="/logo-darkmode.png" alt="logo" className="w-[150px] h-auto" />
      </a>
      <div className="flex flex-row items-center">
        {NavLinks.map((item) => (
          <p key={item.id} className="text-[1rem] mr-10 cursor-pointer">
            {item.id}
          </p>
        ))}
        <Button text="Logout" type="submit" textSize="sm" />
      </div>
    </div>
  );
}
