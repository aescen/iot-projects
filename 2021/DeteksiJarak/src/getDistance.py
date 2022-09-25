def getDistance1(self, midPoints, totalPerson, frame=None):
    # distance using triangle similarity
    # equation 1:
    # Focal Lenght = (Object Height in pixel * Object Distance from camera) / Object Real Height
    # equation 2:
    # Object Distance from camera = (Object Real Height * Focal Length) / Object Height in pixel
    dist = np.zeros((totalPerson, totalPerson))
    for i in range(totalPerson):
        for j in range(i + 1, totalPerson):
            if i != j:
                # pos 1:i
                pos1ToCam = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[i]['height']
                midPoint1_cm = (
                    ( (midPoints[i]['point'][0] * pos1ToCam) / self.args['focalLength'] ), # X
                    ( (midPoints[i]['point'][1] * pos1ToCam) / self.args['focalLength'] ), # Y
                )

                # pos 2:j
                pos2ToCam = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[j]['height']
                midPoint2_cm = (
                    ( (midPoints[j]['point'][0] * pos2ToCam) / self.args['focalLength'] ),
                    ( (midPoints[j]['point'][1] * pos2ToCam) / self.args['focalLength'] ),
                )

                # dst = (a^2 + b^2) ^.5: pythagorean theorem
                X = midPoint1_cm[0] - midPoint2_cm[0]
                Y = midPoint1_cm[1] - midPoint2_cm[1]
                dstA = sqrt(
                    pow( X, 2 ) +
                    pow( Y, 2 )
                )
                dstB = pos1ToCam - pos2ToCam
                dstC = sqrt(
                    pow( dstA, 2 ) +
                    pow( dstB, 2 )
                )
                dist[i][j] = dstC
                self.dstCount += 1

                print(
                    f'frame no: {self.dstCount}',
                    f'0 from camera: {pos1ToCam:.2f}cm',
                    f'1 from camera: {pos2ToCam:.2f}cm',
                    f'dist: {dstC:.2f}cm'
                )

                if not frame is None:
                    cv2.putText(frame, str(f'frame: {self.dstCount} dst: {dstC:.2f}cm'),
                        (int(self.maxWidth * .025), int(self.maxHeight * .1)),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
    return dist

def getDistance2(self, midPoints, totalPerson, frame=None):
    # distance using triangle similarity
    # equation 1:
    # Focal Lenght = (Object Height in pixel * Object Distance from camera) / Object Real Height
    # equation 2:
    # Object Distance from camera = (Object Real Height * Focal Length) / Object Height in pixel
    dist = np.zeros((totalPerson, totalPerson))
    for i in range(totalPerson):
        for j in range(i + 1, totalPerson):
            if i != j:
                # pos 1:i
                dstToCam1 = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[i]['height']
                midPoint1_cm = (
                    ( (midPoints[i]['point'][0] * dstToCam1) / self.args['focalLength'] ), # X
                    ( (midPoints[i]['point'][1] * dstToCam1) / self.args['focalLength'] ), # Y
                )
                
                # pos 2:j
                dstToCam2 = (self.args['objectHeight'] * self.args['focalLength']) / midPoints[j]['height']
                midPoint2_cm = (
                    ( (midPoints[j]['point'][0] * dstToCam2) / self.args['focalLength'] ),
                    ( (midPoints[j]['point'][1] * dstToCam2) / self.args['focalLength'] ),
                )
                # dst = (a^2 + b^2 + c^2) ^.5: pythagorean theorem
                dst = sqrt(
                    pow( midPoint1_cm[0] - midPoint2_cm[0], 2 ) +
                    pow( midPoint1_cm[1] - midPoint2_cm[1], 2 ) +
                    pow( dstToCam1 - dstToCam2, 2 )
                )
                dist[i][j] = dst
                self.dstCount += 1
                print(
                    f'frame no: {self.dstCount}',
                    f'0 from camera: {dstToCam1:.2f}cm',
                    f'1 from camera: {dstToCam2:.2f}cm',
                    f'dist: {dst:.2f}cm'
                )
                if not frame is None:
                    cv2.putText(frame, str(f'frame: {self.dstCount} dst: {dst:.2f}cm'),
                        (int(self.maxWidth * .025), int(self.maxHeight * .1)),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 1)
    return dist