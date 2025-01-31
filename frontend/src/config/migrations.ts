/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import axios from 'axios';
import type { MigrationManifest } from 'redux-persist';
import { createMigrate } from 'redux-persist';
import { Course } from 'types/api';

/**
 * IMPORTANT NOTE:
 *
 * Since we store the state to local storage via redux-persist, this means that
 * any modifications to the state (i.e. changing the initialState data structure
 * fields, a bug created in the reducer functions that can cause some logic
 * issues, etc.) can have unintended effects for users using a previous version local
 * storage data format. This could cause Circles to break or create some weird behaviours.
 *
 * You must update/increment `persistVersion` value in this file to indicate is a breaking
 * change is introduced to make it non compatible with previous versions of local storage data.
 *
 * Create a migration function to translate the old state structure to the new one.
 * Migrations function can be found in `migrations.ts`.
 *
 */

// migration schema used to translate structure - return undefined to reset initialState
const persistMigrations: MigrationManifest = {
  0: () => undefined,
  1: () => undefined,
  2: (oldState) => {
    const newState = { ...oldState };
    newState.degree.specs = [...newState.degree.majors, ...newState.degree.minors];
    delete newState.degree.majors;
    delete newState.degree.minors;
    return newState;
  },
  3: async (oldState) => {
    const newState = { ...oldState };

    const courses = Object.keys(newState.planner.courses);
    await Promise.all(courses.map(async (course) => {
      try {
        const res = await axios.get<Course>(`/courses/getCourse/${course}`);
        if (res.status === 200) {
          const courseData = res.data;
          newState.planner.courses[courseData.code].isMultiterm = courseData.is_multiterm;
        }
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Error at migrations v3', e);
      }
    }));
    return newState;
  },
};

/**
 * IMPORTANT NOTE:
 *
 * Increment `persistVersion` whenever there is an underlying breaking change to the state
 * and alongside it, provide a migration function to translate the old state structure
 * to the new one.
 */
export const persistVersion = 3;

const persistMigrate = createMigrate(persistMigrations);

export default persistMigrate;
