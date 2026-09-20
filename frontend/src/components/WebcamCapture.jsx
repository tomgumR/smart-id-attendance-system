import React, { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'

export default forwardRef(function WebcamCapture({onReady}, ref) {
  const video=useRef(); const stream=useRef(); const [error,setError]=useState('')
  async function start(){try{stream.current=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment',width:{ideal:1280}},audio:false});video.current.srcObject=stream.current; onReady?.(true)}catch(e){setError('Camera permission is unavailable. You can upload an image instead.')}}
  useEffect(()=>()=>stream.current?.getTracks().forEach(t=>t.stop()),[])
  useImperativeHandle(ref,()=>({start,capture(){if(!video.current?.videoWidth)return null;const c=document.createElement('canvas');c.width=video.current.videoWidth;c.height=video.current.videoHeight;c.getContext('2d').drawImage(video.current,0,0);return new Promise(resolve=>c.toBlob(resolve,'image/jpeg',.92))}}))
  return <div className="camera"><video ref={video} autoPlay playsInline/><div className="frame"><i/><i/><i/><i/></div>{!stream.current&&<button className="camera-start" onClick={start}>Start camera</button>}{error&&<div className="camera-error">{error}</div>}</div>
})
