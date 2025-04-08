import React, { useState } from "react";
import "../style/style.css";

export default function AddPopUp({ book, onClose, updateBookshelf, position, currentReading, setCurrentReading }) {
    const handleUpdateBookshelf = async (status) => {
        if (
            status === "currently-reading" &&
            currentReading &&
            (currentReading.id !== book.id && currentReading._id !== book.id)
        ) {
            const confirmReplace = window.confirm(
                `You are already reading "${currentReading.title}". Do you want to replace it and lose progress?`
            );
            if (!confirmReplace) {
                return;
            }
        }
        const response = await updateBookshelf(book, status);
        if (response.ok) {
            alert(`Added to ${status.replace("-", " ")}!`);
            if (status === "currently-reading") {
                setCurrentReading(book);
            }
        } else {
            alert(`Failed to add to ${status.replace("-", " ")}`);
        }
        onClose();
    };

    return (
        <div className="popup-overlay">
            <div className="add-box">
                <button className="add-popup-close" onClick={onClose}> × </button>
                <div className="things-to-add-to">
                    <div className="add-current">
                        <button className="plus-button" onClick={() => handleUpdateBookshelf("currently-reading")}> + </button>
                        <p>Currently Reading</p>
                    </div>
                    <div className="add-to-read">
                        <button className="plus-button" onClick={() => handleUpdateBookshelf("to-read")}> + </button>
                        <p>To-Read Shelf</p>
                    </div>
                    <div className="add-shelf">
                        <button className="plus-button" onClick={() => handleUpdateBookshelf("read")}> + </button>
                        <p>Finished Reading</p>
                    </div>
                </div>
            </div>
        </div>
    );
}


// import React, { useState } from "react";
// import "../style/style.css";

// export default function AddPopUp({
//   book,
//   onClose,
//   updateBookshelf,
//   position,
//   currentReading,
//   setCurrentReading,
// }) {
//   const [showConfirm, setShowConfirm] = useState(false);
//   const [pendingStatus, setPendingStatus] = useState(null);

//   const handleUpdateBookshelf = (status) => {
//     if (
//       status === "currently-reading" &&
//       currentReading &&
//       currentReading.id !== book.id &&
//       currentReading._id !== book.id
//     ) {
//       setPendingStatus(status);
//       setShowConfirm(true);
//     } else {
//       proceedUpdate(status);
//     }
//   };

//   const proceedUpdate = async (statusToUse) => {
//     const response = await updateBookshelf(book, statusToUse);
//     if (response.ok) {
//       if (statusToUse === "currently-reading") {
//         setCurrentReading(book);
//       }
//     } else {
//       console.error(`Failed to add to ${statusToUse}`);
//     }
//     setShowConfirm(false);
//     setPendingStatus(null);
//     onClose();
//   };

//   return (
//     <div className="popup-overlay">
//       <div className="add-box">
//         <button className="add-popup-close" onClick={onClose}>
//           ×
//         </button>
//         <div className="things-to-add-to">
//           <div className="add-current">
//             <button
//               className="plus-button"
//               onClick={() => handleUpdateBookshelf("currently-reading")}
//             >
//               +
//             </button>
//             <p>Currently Reading</p>
//           </div>
//           <div className="add-to-read">
//             <button
//               className="plus-button"
//               onClick={() => handleUpdateBookshelf("to-read")}
//             >
//               +
//             </button>
//             <p>To-Read Shelf</p>
//           </div>
//           <div className="add-shelf">
//             <button
//               className="plus-button"
//               onClick={() => handleUpdateBookshelf("read")}
//             >
//               +
//             </button>
//             <p>Finished Reading</p>
//           </div>
//         </div>
//       </div>

//       {showConfirm && (
//         <div className="modal-overlay">
//           <div className="modal-box">
//             <p>
//               You are already reading <strong>"{currentReading.title}"</strong>.
//               <br />
//               Replace it and lose progress?
//             </p>
//             <div className="modal-actions">
//               <button
//                 className="confirm-button"
//                 onClick={() => proceedUpdate(pendingStatus)}
//               >
//                 Yes, replace
//               </button>
//               <button
//                 className="cancel-button"
//                 onClick={() => {
//                   setShowConfirm(false);
//                   setPendingStatus(null);
//                 }}
//               >
//                 Cancel
//               </button>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }