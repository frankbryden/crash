import moment from 'moment';
export default function parseTimestamp(epoch) {
    return moment(epoch).format("MMMM Do YYYY, hh:mm");
}