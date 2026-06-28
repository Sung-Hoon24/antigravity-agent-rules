import React, { useState, useEffect } from 'react';
// Mock data import (실제로는 API나 Context에서 가져와야 함)
import mockMTP from '../data/mock_mtp_v2.0.json';
import vtmSpecs from '../data/mock_vtm_specs.json';

const VideoFunnelStateMachine = ({ mtpData, vtmSpecsData }) => {
  // [State Management] 현재 재생 중인 세그먼트와 시간 추적
  const [currentTime, setCurrentTime] = useState(0);
  const [currentStateIndex, setCurrentStateIndex] = useState(0);
  const [currentSegment, setCurrentSegment] = useState(mtpData.segments[0]);

  // 🚨 핵심 로직: Time-based State Transition Management
  useEffect(() => {
    if (!mtpData || !mtpData.segments) return;

    let nextStateIndex = currentStateIndex;
    let nextSegment = mtpData.segments[currentStateIndex];
    const intervalTime = 100; // 100ms 마다 상태 검사 (실시간 시뮬레이션)

    // 시간 경과에 따른 State Index 업데이트 로직
    const timer = setInterval(() => {
      setCurrentTime(prevTime => prevTime + intervalTime);
      const currentTimeSeconds = Math.floor(prevTime / 1000);

      if (nextStateIndex < mtpData.segments.length - 1) {
        const nextSegmentInfo = mtpData.segments[nextStateIndex];
        // 다음 세그먼트 시작 시간 도달 체크
        if (currentTimeSeconds >= nextSegmentInfo.timeStart && currentTimeSeconds < nextSegmentInfo.timeEnd) {
          setCurrentSegment(nextSegmentInfo);
          console.log(`[STATE CHANGE] -> ${nextSegmentInfo.state}`);
        } else if (currentTimeSeconds >= nextSegmentInfo.timeEnd) {
          // 다음 세그먼트로 이동
          nextStateIndex++;
          setCurrentStateIndex(nextStateIndex);
          setCurrentSegment(mtpData.segments[nextStateIndex]);
        }
      }

    }, intervalTime);

    return () => clearInterval(timer);
  }, [mtpData, currentStateIndex, currentSegment]);


  // 🎨 VTM (Void Transition Module) 시각화 컴포넌트
  const renderVtmEffect = (currentSegment, nextSegment) => {
    if (!currentSegment || !nextSegment) return null;

    const transitionId = vtmSpecsData['VTM-' + currentSegment.state.replace(/[^A-Z]/g, '')]; // 예시 매칭 로직
    if (!transitionId || !vtmSpecsData[transitionId]) return null;

    const specs = vtmSpecsData[transitionId];
    return (
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 50,
        backgroundColor: `${specs.params.colorStart}AA`, // 애니메이션 효과 시뮬레이션
        transition: `background-color ${specs.params.durationMs / 1000}s ease`
      }}>
        {/* 실제로는 CSS Keyframe Animation이나 WebGL이 사용되어야 함 */}
        <p style={{ color: 'white', padding: '20px' }}>[VTM Active] {specs.logic}</p>
      </div>
    );
  };


  // 🖥️ 메인 렌더링 로직 (Prototype UI)
  return (
    <div style={styles.container}>
        {/* VTM 오버레이 영역 */}
        {renderVtmEffect(currentSegment, mtpData.segments[currentStateIndex + 1])}

        <div style={styles.videoArea}>
            <h2>Current State: {currentSegment.state}</h2>
            <p>{currentSegment.content}</p>
            <div className="timeline-progress" style={{ width: `${(currentTime / mtpData.durationSec) * 100}%` }}></div>
        </div>

        {/* 디버깅 및 상태 정보 패널 */}
        <div style={styles.debugPanel}>
            <h3>[System Debug]</h3>
            <p>Time Elapsed: {Math.floor(currentTime / 1000)}s</p>
            <p>Current State Index: {currentStateIndex}</p>
            {currentSegment.conflictType === "Void Transition" ? (
                <button style={styles.gapButton}>⚡️ LOGICAL GAP DETECTED! VTM Activate</button>
            ) : <div />}
        </div>
    </div>
  );
};

// 가상의 스타일링 객체 (실제 CSS 파일로 분리 권장)
const styles = {
  container: { fontFamily: 'Arial, sans-serif', padding: '20px', border: '1px solid #ccc' },
  videoArea: { position: 'relative', width: '90%', height: '400px', background: '#111', color: 'white', margin: '20px 0', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' },
  debugPanel: { padding: '15px', border: '1px solid #eee', backgroundColor: '#f9f9f9' },
  gapButton: { padding: '10px 20px', cursor: 'pointer', backgroundColor: '#a30046', color: 'white', border: 'none', borderRadius: '5px' }
};

export default VideoFunnelStateMachine;
