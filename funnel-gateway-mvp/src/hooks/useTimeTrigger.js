import { useState, useEffect, useCallback } from 'react';

/**
 * @description 특정 타이밍(T+ms)에 이벤트 발생 여부를 체크하는 커스텀 훅.
 * @param {number} triggerTime - 트리거가 작동해야 하는 절대 시간 (밀리초).
 * @param {number} toleranceMs - 허용 오차 범위 (±ms).
 * @returns {boolean} - 현재 시간이 트랜지션 조건 내에 있는지 여부.
 */
const useTimeTrigger = (triggerTime, toleranceMs = 50) => {
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    // 타이머를 사용하여 지속적으로 상태를 체크합니다.
    let intervalId = setInterval(() => {
      const currentTime = performance.now();
      const timeDifference = Math.abs((currentTime - triggerTime) / 1000); // 시간 차이 계산

      if (timeDifference <= toleranceMs / 1000) {
        setIsActive(true);
        clearInterval(intervalId); // 성공적으로 감지되면 인터벌 중단
      } else if (timeDifference > 500) {
         // 너무 오래 지나면 상태 초기화 (방지용)
        setIsActive(false);
      }
    }, 20); // 20ms 간격으로 체크하여 정밀도 확보

    return () => clearInterval(intervalId);
  }, [triggerTime, toleranceMs]);

  return isActive;
};

export default useTimeTrigger;
