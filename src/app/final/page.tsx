"use client"

import React from 'react'
import { useEffect, useState } from 'react';

export default function final() {
  const [selectedRowsFinal, setSelectedRowsFinal] = useState([]);
  useEffect(() => {
    const storedRows = localStorage.getItem('selectedForCurate');
    if (storedRows) {
      setSelectedRowsFinal(JSON.parse(storedRows));
    };
  }, []);
  console.log(selectedRowsFinal);
  return (
    <div>final</div>
  )
}
