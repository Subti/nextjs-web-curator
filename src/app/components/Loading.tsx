import React from "react";

interface LoadingProps {
  text: string;
}

const Loading = ({ text }: LoadingProps) => {
  return (
    <div className="fixed top-0 left-0 w-screen h-screen z-50 flex justify-center items-center bg-gray-900 bg-opacity-75">
      <div className="flex flex-col gap-10 items-center justify-center">
        <h1 className="text-white text-[2rem]">{text}</h1>
        <div className="loader border-t-qoherentblue border-b-qoherentpurple border-l-transparent border-r-transparent ease-linear rounded-full border-8 h-24 w-24"></div>
      </div>
    </div>
  );
};

export default Loading;
